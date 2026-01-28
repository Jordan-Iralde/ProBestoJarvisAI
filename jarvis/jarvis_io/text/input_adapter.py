# io/text/input_adapter.py
"""Text input adapter for CLI"""

import time
from typing import Optional


class CLIInput:
    def __init__(self, eventbus, nlu_pipeline=None, logger=None, core=None):
        self.bus = eventbus
        self.nlu = nlu_pipeline
        self.logger = logger
        self.core = core  # Reference to JarvisCore for enhanced features
        self._running = True
        self._last_command_time = time.time()
        self._command_count = 0

    def process_text(self, text: str):
        """
        Process text input directly
        Required by diagnostics and API
        """
        if not text or not text.strip():
            return
        
        text = text.strip()
        self._command_count += 1
        self._last_command_time = time.time()
        
        # Emit text input event
        self.bus.emit("input.text", {"text": text})
        
        # Process with NLU
        if self.nlu:
            self.nlu.process(text, self.bus)

    def poll(self):
        if not self._ready():
            return

        try:
            # Enhanced prompt with system status
            prompt = self._build_prompt()
            txt = input(prompt).strip()

            if txt:
                self._command_count += 1
                self._last_command_time = time.time()

                # Special commands
                if txt.lower() in ['help', 'ayuda', '?']:
                    self._show_help()
                    return
                elif txt.lower() in ['status', 'estado']:
                    self._show_status()
                    return
                elif txt.lower() in ['skills', 'habilidades']:
                    self._show_skills()
                    return
                elif txt.lower() in ['quit', 'exit', 'salir']:
                    self._running = False
                    return

                # Emitir evento de input
                self.bus.emit("input.text", {"text": txt})

                # Procesar con NLU si está disponible
                if self.nlu:
                    self.nlu.process(txt, self.bus)
                else:
                    if self.logger:
                        self.logger.warning("NLU pipeline no disponible")
                    else:
                        print("[WARN] NLU pipeline no disponible")
        except EOFError:
            self._running = False
        except KeyboardInterrupt:
            self._running = False

    def _build_prompt(self) -> str:
        """Build enhanced prompt with system information"""
        base_prompt = "Jarvis"

        # Add session info if core is available
        if self.core:
            try:
                # Get session insights for quick status
                insights = self.core.get_session_insights()
                confidence = insights.get('confidence', 0)

                # Color coding based on confidence
                if confidence > 0.8:
                    status_indicator = "🟢"  # High confidence
                elif confidence > 0.5:
                    status_indicator = "🟡"  # Medium confidence
                else:
                    status_indicator = "🔴"  # Low confidence

                base_prompt += f" {status_indicator}"

                # Add command count
                base_prompt += f" [{self._command_count}]"

            except:
                base_prompt += " ⚪"  # Neutral status

        return f"{base_prompt} >> "

    def _show_help(self):
        """Show available commands and help"""
        help_text = """
🤖 Jarvis AI Assistant - Comandos Disponibles
==========================================

📝 COMANDOS BÁSICOS:
  • [cualquier texto]     - Procesar con IA o ejecutar skill
  • help/ayuda/?          - Mostrar esta ayuda
  • status/estado         - Ver estado del sistema
  • skills/habilidades    - Ver skills disponibles
  • quit/exit/salir       - Salir del sistema

🧠 SKILLS INTELIGENTES (Ej.):
  • qué hora es?          - Obtener hora actual
  • busca archivo X       - Buscar archivos
  • estado del sistema    - Ver estado del PC
  • abrir notepad         - Ejecutar aplicación
  • crear nota            - Crear nota rápida
  • recordatorio          - Establecer recordatorio

⚙️  INFORMACIÓN DEL SISTEMA:
  • estado                - Ver información de sesión
  • skills                - Listar skills registrados
"""
        print(help_text)

    def _show_status(self):
        """Show system status"""
        if self.core:
            try:
                insights = self.core.get_session_insights()
                print("\n📊 Estado de la Sesión:")
                print(f"  • Confianza: {insights.get('confidence', 0):.1%}")
                print(f"  • Comandos: {self._command_count}")
                print(f"  • Últimas intents: {insights.get('recent_intents', [])[:3]}")
            except Exception as e:
                print(f"Error al obtener estado: {e}")
        else:
            print(f"\n📊 Status:")
            print(f"  • Comandos: {self._command_count}")
            print(f"  • Tiempo: {time.time() - self._last_command_time:.1f}s desde último comando")

    def _show_skills(self):
        """Show available skills"""
        if self.core:
            try:
                skills = self.core.get_available_skills()
                print("\n🧠 Skills Disponibles:")
                for skill in skills:
                    print(f"  • {skill}")
            except Exception as e:
                print(f"Error al obtener skills: {e}")
        else:
            print("Core no disponible")

    def _ready(self) -> bool:
        """Check if ready to accept input"""
        return self._running

    @property
    def running(self) -> bool:
        return self._running

    def stop(self):
        """Stop input processing"""
        self._running = False