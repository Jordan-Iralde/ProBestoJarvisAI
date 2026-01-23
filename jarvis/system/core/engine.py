# system/core/engine.py
import time
from typing import Optional

from system.runtime.state import RuntimeState
from system.runtime.events import EventBus
from system.runtime.scheduler import Scheduler
from system.boot.initializer import Initializer
from system.boot.diagnostics import Diagnostics
from system.boot.loader import ModuleLoader

from interface.text.input_adapter import CLIInput
from interface.text.output_adapter import TextOutput
from interface.speech.tts import TTS
from interface.speech.stt import VoskSTT
from brain.nlu.pipeline import NLUPipeline

from skills.system.logging.manager import JarvisLogger
from data.collector import DataCollector
from skills.actions.dispatcher import SkillDispatcher
from skills.get_time import GetTimeSkill
from skills.system_status import SystemStatusSkill
from skills.create_note import CreateNoteSkill
from skills.search_file import SearchFileSkill
from skills.summarize_recent_activity import SummarizeRecentActivitySkill
from skills.analyze_session_value import AnalyzeSessionValueSkill
from skills.research_and_contextualize import ResearchAndContextualizeSkill
from skills.analyze_system_health import AnalyzeSystemHealthSkill
from skills.what_do_you_know_about_me import WhatDoYouKnowAboutMeSkill
from skills.evaluate_user_session import EvaluateUserSessionSkill
from skills.system_auto_optimization import SystemAutoOptimizationSkill
from skills.auto_programming import AutoProgrammingSkill

# Web Dashboard (opcional)
try:
    from webapp.dashboard import JarvisDashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    JarvisDashboard = None

from .handlers import CoreHandlers
from .responses import ResponseFormatter

from system.constants import (
    EVENT_NLU_INTENT, EVENT_INPUT_TEXT, EVENT_INPUT_VOICE, EVENT_JARVIS_RESPONSE
)

# New: Memory and LLM components
from brain.memory.storage import JarvisStorage
from brain.memory.context import ContextManager
from brain.llm.manager import LLMManager
from brain.reflection_engine import ActiveLearningEngine


class JarvisCore:
    """
    Jarvis Core v2 - Refinado para escalabilidad
    """
    def __init__(self, config: dict):
        self.config = config
        self.start_time = time.time()
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
        
        # STT (offline, Vosk) con wake word obligatoria
        self.stt = VoskSTT()
        
        # New: Memory and LLM components
        self.storage = JarvisStorage()
        self.context_manager = ContextManager(self.storage)
        self.llm_manager = LLMManager()

        # NLU Pipeline (temporal - será inicializado en boot si es necesario)
        self.nlu = None

        # Active Learning Engine - Observes and learns from user patterns
        self.active_learning = ActiveLearningEngine(
            storage=self.storage,
            nlu_parser=self.nlu,
            logger=self.logger.logger
        )

        # Dispatcher de skills
        self.skill_dispatcher = SkillDispatcher(logger=self.logger.logger)
        self._register_skills()

        # NLU Pipeline - inicializar después de registrar skills
        self.nlu = NLUPipeline(self.skill_dispatcher.skills, debug=config.get("debug_nlu", False))

        # Actualizar active_learning con NLU
        self.active_learning.nlu_parser = self.nlu
        
        # Formateador de respuestas
        self.response_formatter = ResponseFormatter()
        
        # Handlers
        self.handlers = CoreHandlers(self)
        
        # Suscripciones a eventos
        self.events.subscribe(EVENT_NLU_INTENT, self.handlers.handle_skill_intent)
        self.events.subscribe(EVENT_INPUT_TEXT, self.handlers.handle_input_text)
        self.events.subscribe(EVENT_INPUT_VOICE, self.handlers.handle_input_voice)
        self.events.subscribe(EVENT_JARVIS_RESPONSE, self.handlers.handle_response)
        
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

    def _register_skills(self):
        """Registra todas las skills disponibles"""
        from skills.open_app import OpenAppSkill
        from skills.get_time import GetTimeSkill
        from skills.system_status import SystemStatusSkill
        from skills.create_note import CreateNoteSkill
        from skills.search_file import SearchFileSkill
        from skills.summarize_recent_activity import SummarizeRecentActivitySkill
        from skills.summarize_last_session import SummarizeLastSessionSkill
        from skills.analyze_session_value import AnalyzeSessionValueSkill
        from skills.research_and_contextualize import ResearchAndContextualizeSkill
        from skills.analyze_system_health import AnalyzeSystemHealthSkill
        from skills.what_do_you_know_about_me import WhatDoYouKnowAboutMeSkill
        from skills.evaluate_user_session import EvaluateUserSessionSkill
        
        skills = {
            "open_app": OpenAppSkill,
            "get_time": GetTimeSkill,
            "system_status": SystemStatusSkill,
            "create_note": CreateNoteSkill,
            "search_file": SearchFileSkill,
            "summarize_recent_activity": SummarizeRecentActivitySkill,
            "summarize_last_session": SummarizeLastSessionSkill,
            "analyze_session_value": AnalyzeSessionValueSkill,
            "research_and_contextualize": ResearchAndContextualizeSkill(self.storage, self.llm_manager),
            "analyze_system_health": AnalyzeSystemHealthSkill(self.logger.logger),
            "what_do_you_know_about_me": WhatDoYouKnowAboutMeSkill(self.storage, self.active_learning),
            "evaluate_user_session": EvaluateUserSessionSkill(self.storage, self.active_learning),
            "auto_programming": AutoProgrammingSkill(self.storage, self.active_learning, self.logger.logger),
            "system_auto_optimization": SystemAutoOptimizationSkill(self.logger.logger)
        }
        
        for name, skill_cls in skills.items():
            # Handle skills that are already instantiated
            if hasattr(skill_cls, 'run'):
                self.skill_dispatcher.register(name, skill_cls)
            else:
                # Instantiate skills that need it
                skill_instance = skill_cls()
                self.skill_dispatcher.register(name, skill_instance)
        
        self.logger.logger.info(f"Registered {len(skills)} skills")

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

            # Inicializar Input adapter
            self.logger.logger.info("Initializing Input adapter...")
            self.input = CLIInput(self.events, nlu_pipeline=self.nlu, logger=self.logger.logger, core=self)

            self.logger.logger.info("Running diagnostics...")
            self._diagnostics.run()
            
            self.state.set("READY")
            self.logger.logger.info("✓ Boot completed - READY")
            
            # Iniciar STT si está disponible
            if self.stt.start(self.events):
                self.logger.logger.info("[STT] Offline STT started (wake word: jarvis)")
            else:
                self.logger.logger.warning("[STT] STT not available (install vosk & sounddevice)")

            # Iniciar Dashboard Web si está habilitado
            if DASHBOARD_AVAILABLE and self.config.get("web_dashboard", False):
                self.logger.logger.info("Starting Web Dashboard...")
                self.dashboard = JarvisDashboard(self)
                dashboard_port = self.config.get("dashboard_port", 5000)
                if self.dashboard.start(port=dashboard_port):
                    self.logger.logger.info(f"[WEB] Dashboard started on port {dashboard_port}")
                else:
                    self.logger.logger.warning("[WEB] Failed to start dashboard")
            else:
                self.dashboard = None
                if self.config.get("web_dashboard", False):
                    self.logger.logger.warning("[WEB] Dashboard requested but not available (missing flask)")

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
            
            # Detener STT si está corriendo
            try:
                self.stt.stop()
            except Exception as e:
                self.logger.log_error("STT_STOP_ERR", str(e))
            
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
    
    def get_session_insights(self) -> dict:
        """Obtener insights de aprendizaje de la sesión actual usando active learning"""
        return self.active_learning.learn_from_session(self.start_time)
    
    def get_usage_stats(self) -> dict:
        """Obtener estadísticas generales de uso"""
        return self.active_learning.get_usage_stats()
    
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
