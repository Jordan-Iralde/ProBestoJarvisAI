# system/core.py v2 - Refinado
import time
import traceback
import asyncio
from typing import Optional
from datetime import datetime

from system.runtime.state import RuntimeState
from system.runtime.events import EventBus
from system.runtime.scheduler import Scheduler
from system.boot.initializer import Initializer
from system.boot.diagnostics import Diagnostics
from system.boot.loader import ModuleLoader

from interface.text.input_adapter import CLIInput
from interface.text.output_adapter import TextOutput
from interface.speech.tts import TTS
from brain.nlu.pipeline import NLUPipeline

# Sistema de logging profesional
from skills.system.logging.manager import JarvisLogger
from data.collector import DataCollector

# Skill dispatcher
from skills.actions.dispatcher import SkillDispatcher

# Skills
from skills.open_app import OpenAppSkill
from skills.get_time import GetTimeSkill
from skills.system_status import SystemStatusSkill
from skills.create_note import CreateNoteSkill
from skills.search_file import SearchFileSkill


class JarvisCore:
    """
    Jarvis Core v2 - Refinado para escalabilidad
    
    Features:
    - Logging profesional (no más prints)
    - Data collection transparente
    - Async support
    - Hot-reload config
    - Métricas en tiempo real
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.state = RuntimeState()
        
        # Sistema de logging profesional
        self.logger = JarvisLogger(config)
        
        # Data collector (con consent del config)
        self.data_collector = DataCollector(
            consent=config.get("data_collection", False)
        )
        
        # Runtime components
        self.events = EventBus(workers=config.get("workers", 4))
        self.scheduler = Scheduler()
        self.modules_loader = ModuleLoader(self)

        # Output adapters
        self.output = TextOutput()
        self.tts = TTS(enabled=bool(config.get("tts", False)))
        
        # Dispatcher de skills
        self.skill_dispatcher = SkillDispatcher(logger=self.logger.logger)
        self._register_skills()
        
        # NLU Pipeline con registry
        self.nlu = NLUPipeline(
            skills_registry=self.skill_dispatcher.skills,
            debug=self.config.get("debug_nlu", False)
        )
        
        # Input adapter
        self.input = CLIInput(self.events, nlu_pipeline=self.nlu, logger=self.logger.logger)
        
        # Suscripciones a eventos
        self.events.subscribe("nlu.intent", self._handle_skill_intent)
        self.events.subscribe("input.text", self._handle_input_text)
        self.events.subscribe("jarvis.response", self._handle_response)
        
        # Boot components
        self._initializer = Initializer(self)
        self._diagnostics = Diagnostics(self)
        
        # Historial de comandos (para patrones)
        self.command_history = []

        # Short-term memory (fase 1): últimas interacciones para contexto simple
        self.short_term_memory = []
        self.short_term_memory_max = int(config.get("short_term_memory_max", 20))
        
        self.logger.logger.info("JarvisCore v2 initialized")

    def _log(self, tag: str, msg: str):
        """Logging interno usado por módulos de boot (initializer/loader/diagnostics)."""
        try:
            self.logger.logger.info(f"[{tag}] {msg}")
        except Exception:
            print(f"[{tag}] {msg}")

    def _format_response(self, intent: str, dispatch_result: dict) -> str:
        if not intent:
            return "No recibí ninguna intención."

        if intent == "unknown":
            available = self.skill_dispatcher.list_skills()
            return "No entendí el comando. Probá con: " + ", ".join(available)

        if not dispatch_result.get("success", True):
            err = dispatch_result.get("error") or "error"
            return f"No pude ejecutar '{intent}': {err}"

        payload = dispatch_result.get("result")
        if isinstance(payload, dict) and payload.get("success") is False:
            err = payload.get("error") or "error"
            return f"No pude ejecutar '{intent}': {err}"

        if intent == "open_app" and isinstance(payload, dict):
            return f"Abriendo {payload.get('app', 'la aplicación')}."
        if intent == "get_time" and isinstance(payload, dict):
            return f"Son las {payload.get('time')} del {payload.get('date')}."
        if intent == "system_status" and isinstance(payload, dict):
            cpu = (payload.get("cpu") or {}).get("percent")
            mem = (payload.get("memory") or {}).get("percent")
            if cpu is not None and mem is not None:
                return f"Estado del sistema: CPU {cpu}% | RAM {mem}%."
            return "Estado del sistema obtenido."
        if intent == "create_note" and isinstance(payload, dict):
            return f"Nota creada: {payload.get('filename', 'ok')}."
        if intent == "search_file" and isinstance(payload, dict):
            return f"Búsqueda completada. Encontré {payload.get('count', 0)} resultados."

        return f"Listo: {intent}."

    def _handle_response(self, event):
        data = event.get("data", {}) if isinstance(event, dict) else {}
        text = data.get("text")
        if not text:
            return
        self.output.send(text)
        self.tts.speak(text)
    
    def _register_skills(self):
        """Registra todas las skills disponibles"""
        skills = {
            "open_app": OpenAppSkill,
            "get_time": GetTimeSkill,
            "system_status": SystemStatusSkill,
            "create_note": CreateNoteSkill,
            "search_file": SearchFileSkill
        }
        
        for name, skill_cls in skills.items():
            self.skill_dispatcher.register(name, skill_cls)
        
        self.logger.logger.info(f"Registered {len(skills)} skills")
    
    def _handle_input_text(self, event):
        """Handler para texto de entrada"""
        text = event.get("data", {}).get("text", "")
        if text:
            self.command_history.append(text)
            
            # Mantener solo últimos 100
            if len(self.command_history) > 100:
                self.command_history.pop(0)
            
            # Detectar patrones cada 10 comandos
            if len(self.command_history) % 10 == 0:
                patterns = self.data_collector.detect_pattern(self.command_history)
                if patterns:
                    self.logger.logger.info(f"Patterns detected: {patterns}")
    
    def _handle_skill_intent(self, event):
        """Handler para intents procesados por NLU"""
        start_time = time.time()
        
        try:
            payload = event.get("data", {})
            
            intent = payload.get("intent")
            entities = payload.get("entities", {})
            raw_text = payload.get("raw", "")
            
            if not intent:
                self.logger.logger.warning("Empty intent received")
                return
            
            # Log comando
            self.logger.logger.debug(f"Processing intent: {intent} | entities: {entities}")
            
            # Dispatch a la skill
            result = self.skill_dispatcher.dispatch(intent, entities, self.state)

            response_text = self._format_response(intent, result)
            self.events.emit("jarvis.response", {
                "text": response_text,
                "intent": intent,
                "entities": entities
            })

            payload_result = result.get("result") if isinstance(result, dict) else None

            # Guardar contexto mínimo (short-term memory)
            self.short_term_memory.append({
                "intent": intent,
                "entities": entities,
                "raw": raw_text,
                "response": response_text
            })
            if len(self.short_term_memory) > self.short_term_memory_max:
                self.short_term_memory = self.short_term_memory[-self.short_term_memory_max:]
            self.events.emit("memory.short_term.updated", {
                "size": len(self.short_term_memory),
                "last": self.short_term_memory[-1] if self.short_term_memory else None
            })
            
            # Calcular duración
            duration = time.time() - start_time

            # Logs y métricas
            success = True
            if isinstance(result, dict) and result.get("success") is False:
                success = False
            if isinstance(payload_result, dict) and payload_result.get("success") is False:
                success = False
            
            self.logger.log_command(raw_text, intent, entities, success)
            self.logger.log_skill_execution(intent, result, duration)
            
            # Track app usage si es open_app
            if intent == "open_app" and success:
                app_name = None
                if isinstance(payload_result, dict):
                    app_name = payload_result.get("app")
                if not app_name and isinstance(entities.get("app"), list) and len(entities.get("app")) > 0:
                    app_name = entities.get("app")[0]
                if app_name:
                    self.data_collector.track_app_usage(app_name)
            
            if success:
                self.logger.logger.info(f"✓ {intent} executed ({duration:.3f}s)")
            else:
                self.logger.logger.warning(f"✗ {intent} failed")
        
        except Exception as e:
            self.logger.log_error("SKILL_EXECUTION_ERROR", str(e), {
                "intent": intent,
                "entities": entities
            })
            self.logger.logger.error(f"Skill execution error: {e}")
            if self.config.get("debug_errors", True):
                traceback.print_exc()
    
    def boot(self):
        """Secuencia de arranque del sistema"""
        try:
            self.state.set("BOOTING")
            self.logger.logger.info("🚀 Starting boot sequence")
            
            # Iniciar componentes
            self.logger.logger.info("Starting EventBus...")
            self.events.start()
            
            self.logger.logger.info("Starting Scheduler...")
            self.scheduler.start()
            
            # Scheduler: Recolectar métricas cada 5 minutos
            if self.config.get("data_collection", False):
                self.scheduler.schedule_every(300, self.data_collector.collect_system_snapshot)
            
            self.logger.logger.info("Running initializers...")
            self._initializer.run()
            
            self.logger.logger.info("Loading modules...")
            self.modules_loader.load_all()
            
            self.logger.logger.info("Running diagnostics...")
            self._diagnostics.run()
            
            self.state.set("READY")
            self.logger.logger.info("✓ Boot completed - READY")
            
            # Mostrar sugerencias si hay
            suggestions = self.data_collector.get_suggestions()
            if suggestions:
                print("\n💡 Sugerencias basadas en tu uso:")
                for s in suggestions:
                    print(f"   {s}")
                print()
            
        except Exception as e:
            self.logger.log_error("BOOT_FAILED", str(e))
            self.logger.logger.critical(f"Boot failed: {e}")
            self.state.set("DEAD")
            raise
    
    def run(self):
        """Loop principal del sistema"""
        if not self.state.wait_ready(timeout=5.0):
            raise RuntimeError("Core not ready to run")
        
        self.state.set("RUNNING")
        self.logger.logger.info("▶ Main loop started")
        print("\n" + "="*60)
        print("JARVIS está listo. Escribe comandos (Ctrl+C para salir)")
        print("Datos guardados en: Desktop/JarvisData/")
        print("="*60 + "\n")
        
        try:
            while self.state.is_running():
                try:
                    self.input.poll()
                    time.sleep(0.01)
                except KeyboardInterrupt:
                    print("\n[SYSTEM] Interrupción detectada")
                    break
                except Exception as e:
                    self.logger.log_error("CORE_LOOP_ERROR", str(e))
                    if self.config.get("crash_on_error", False):
                        break
        finally:
            self.stop()
    
    def stop(self):
        """Apagado limpio del sistema"""
        cur = self.state.get()
        if cur in ("STOPPING", "DEAD"):
            return
        
        self.logger.logger.info("🛑 Shutting down...")
        self.state.set("STOPPING")
        
        try:
            # Guardar métricas finales
            self.logger.save_metrics()
            
            # Detener componentes
            try: 
                self.input.stop()
            except Exception as e: 
                self.logger.log_error("INPUT_STOP_ERR", str(e))
            
            try: 
                self.modules_loader.stop_all()
            except Exception as e: 
                self.logger.log_error("MODULES_STOP_ERR", str(e))
            
            try: 
                self.scheduler.stop()
            except Exception as e: 
                self.logger.log_error("SCHED_STOP_ERR", str(e))
            
            try: 
                self.events.stop()
            except Exception as e: 
                self.logger.log_error("EVENTS_STOP_ERR", str(e))
        
        finally:
            self.state.set("DEAD")
            self.logger.logger.info("✓ Shutdown complete")
            print("\n👋 Hasta luego!")
    
    def reload_config(self, new_config: dict):
        """Hot-reload de configuración"""
        self.logger.logger.info("Reloading configuration...")
        self.config.update(new_config)
        
        # Recargar componentes que dependen de config
        if "debug_nlu" in new_config:
            self.nlu.debug = new_config["debug_nlu"]
        
        if "data_collection" in new_config:
            self.data_collector.consent = new_config["data_collection"]
        
        self.logger.logger.info("Configuration reloaded")