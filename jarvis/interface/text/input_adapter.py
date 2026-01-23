# interface/text/input_adapter.py
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

🧠 SKILLS INTELIGENTES:
  • qué hora es           - Obtener hora y fecha
  • abre [app]            - Abrir aplicación
  • estado del sistema    - Ver métricas del sistema
  • crea una nota [texto] - Crear nota
  • busca [archivo]       - Buscar archivos
  • resume actividad      - Resumir sesión reciente
  • analiza valor sesión  - Analizar valor de la sesión
  • investiga [tema]      - Buscar información
  • analiza salud sistema - Análisis completo del sistema
  • qué sabes de mí       - Perfil de usuario
  • evalúa sesión         - Coaching de sesión
  • auto programa [cmd]   - Auto-programación

💡 EJEMPLOS:
  • "qué hora es"
  • "abre el navegador"
  • "estado del sistema"
  • "investiga cómo optimizar Windows"
  • "analiza salud sistema"
  • "qué sabes de mí"
  • "evalúa sesión"
  • "auto programa generate_skill nombre_skill descripción"

🔧 SISTEMA:
  • Memoria persistente: SQLite
  • Aprendizaje activo: Análisis continuo
  • Control humano: Todas las acciones requieren aprobación
  • Local-first: Sin dependencias externas para funcionalidad core

Presiona Enter para continuar...
"""
        print(help_text)
        input()

    def _show_status(self):
        """Show system status"""
        if not self.core:
            print("❌ Información del sistema no disponible")
            return

        try:
            # Get system health
            health = self.core.skill_dispatcher.dispatch("analyze_system_health", "general")
            if health and health.get("success"):
                analysis = health["analysis"]
                print(f"""
🏥 Estado del Sistema Jarvis
===========================

💚 Salud General: {analysis['health_score']}/100
⏱️  Tiempo Activo: {time.time() - self.core.start_time:.0f}s
📊 Interacciones: {self._command_count}
🧠 Confianza IA: {self.core.get_session_insights().get('confidence', 0):.1%}

💾 Memoria:
  • Usada: {analysis['resource_usage']['memory']['percent']}%
  • Disponible: {analysis['resource_usage']['memory']['available'] // (1024**3)}GB

⚡ CPU: {analysis['resource_usage']['cpu_percent']}%

📁 Disco: {analysis['resource_usage']['disk']['percent']}%
""")

                if analysis['issues']:
                    print("⚠️  Problemas Detectados:")
                    for issue in analysis['issues'][:3]:
                        print(f"  • {issue['description']}")

                if analysis['recommendations']:
                    print("💡 Recomendaciones:")
                    for rec in analysis['recommendations'][:3]:
                        print(f"  • {rec['action']}")

            else:
                print("❌ Error obteniendo estado del sistema")

        except Exception as e:
            print(f"❌ Error mostrando estado: {e}")

    def _show_skills(self):
        """Show available skills"""
        if not self.core or not hasattr(self.core, 'skill_dispatcher'):
            print("❌ Skills no disponibles")
            return

        skills = list(self.core.skill_dispatcher.skills.keys())
        print(f"""
🛠️ Skills Disponibles ({len(skills)})
==========================

🤖 CORE SKILLS:
""")

        # Categorize skills
        categories = {
            "⏰ Tiempo": ["get_time"],
            "🖥️ Sistema": ["system_status", "open_app", "analyze_system_health"],
            "📝 Productividad": ["create_note", "search_file"],
            "🧠 Inteligencia": ["summarize_recent_activity", "summarize_last_session", "analyze_session_value"],
            "🔍 Investigación": ["research_and_contextualize"],
            "👤 Usuario": ["what_do_you_know_about_me", "evaluate_user_session"],
            "⚙️ Auto-Programación": ["auto_programming"]
        }

        for category, skill_list in categories.items():
            available = [s for s in skill_list if s in skills]
            if available:
                print(f"  {category}:")
                for skill in available:
                    print(f"    • {skill.replace('_', ' ')}")
                print()

        print("💡 Usa 'help' para ver ejemplos de uso")

    def _ready(self):
        return self._running

    def stop(self):
        self._running = False
