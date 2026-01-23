# system/core/handlers.py
import time
import traceback
from typing import Any

from system.constants import EVENT_JARVIS_RESPONSE, EVENT_MEMORY_SHORT_TERM_UPDATED


class CoreHandlers:
    """Handlers de eventos del core, separados para escalabilidad"""
    def __init__(self, core):
        self.core = core

    def handle_response(self, event):
        data = event.get("data", {}) if isinstance(event, dict) else {}
        text = data.get("text")
        if not text:
            return
        self.core.output.send(text)
        self.core.tts.speak(text)

    def handle_input_voice(self, event):
        """Handler para entrada de voz (STT offline)"""
        text = event.get("data", {}).get("text", "")
        if text:
            self.core.logger.logger.info(f"[VOICE] {text}")
            # Reutilizar pipeline de NLU como si fuera texto
            self.core.nlu.process(text, self.core.events)

    def handle_input_text(self, event):
        """Handler para texto de entrada"""
        text = event.get("data", {}).get("text", "")
        if text:
            self.core.command_history.append(text)
            
            # Mantener solo últimos 100
            if len(self.core.command_history) > 100:
                self.core.command_history.pop(0)
            
            # Detectar patrones cada 10 comandos
            if len(self.core.command_history) % 10 == 0:
                patterns = self.core.data_collector.detect_pattern(self.core.command_history)
                if patterns:
                    self.core.logger.logger.info(f"Patterns detected: {patterns}")

    def handle_skill_intent(self, event):
        """Handler para intents procesados por NLU"""
        start_time = time.time()
        intent = None
        entities = {}
        raw_text = ""
        try:
            payload = event.get("data", {})
            
            intent = payload.get("intent")
            entities = payload.get("entities", {})
            raw_text = payload.get("raw", "")
            
            if not intent:
                self.core.logger.logger.warning("Empty intent received")
                return
            
            # Log comando
            self.core.logger.logger.debug(f"Processing intent: {intent} | entities: {entities}")
            
            if intent == "unknown":
                # Use LLM for unknown intents
                context = self.core.context_manager.get_context()
                response_text = self.core.llm_manager.generate(raw_text, context)
                source = "llm"
            else:
                # Dispatch to skill
                result = self.core.skill_dispatcher.dispatch(intent, entities, self.core)
                response_text = self.core.response_formatter.format(intent, result)
                payload_result = result.get("result") if isinstance(result, dict) else None
                source = "skill"
            
            self.core.events.emit(EVENT_JARVIS_RESPONSE, {
                "text": response_text,
                "intent": intent,
                "entities": entities
            })

            # Persist conversation in SQLite
            self.core.storage.save_conversation(raw_text, response_text, source)

            # Guardar contexto mínimo (short-term memory)
            self.core.short_term_memory.append({
                "intent": intent,
                "entities": entities,
                "raw": raw_text,
                "response": response_text
            })
            if len(self.core.short_term_memory) > self.core.short_term_memory_max:
                self.core.short_term_memory = self.core.short_term_memory[-self.core.short_term_memory_max:]
            self.core.events.emit(EVENT_MEMORY_SHORT_TERM_UPDATED, {
                "size": len(self.core.short_term_memory),
                "last": self.core.short_term_memory[-1] if self.core.short_term_memory else None
            })
            
            # Calcular duración
            duration = time.time() - start_time

            # Logs y métricas
            success = True
            if source == "skill":
                if isinstance(result, dict) and result.get("success") is False:
                    success = False
                if isinstance(payload_result, dict) and payload_result.get("success") is False:
                    success = False
                self.core.logger.log_skill_execution(intent, result, duration)
            
            self.core.logger.log_command(raw_text, intent, entities, success)
            
            # Track app usage si es open_app
            if intent == "open_app" and success:
                app_name = None
                if isinstance(payload_result, dict):
                    app_name = payload_result.get("app")
                if not app_name and isinstance(entities.get("app"), list) and len(entities.get("app")) > 0:
                    app_name = entities.get("app")[0]
                if app_name:
                    self.core.data_collector.track_app_usage(app_name)
            
            if success:
                self.core.logger.logger.info(f"✓ {intent} executed ({duration:.3f}s)")
            else:
                self.core.logger.logger.warning(f"✗ {intent} failed")
        
        except Exception as e:
            self.core.logger.log_error("SKILL_EXECUTION_ERROR", str(e), {
                "intent": intent,
                "entities": entities
            })
            self.core.logger.logger.error(f"Skill execution error: {e}")
            if self.core.config.get("debug_errors", True):
                traceback.print_exc()
