# io/cli/interface.py
"""
Advanced CLI Interface for JarvisAI v0.0.4
Structured output with colors, sections, and clear separation.
"""

import sys
from typing import Dict, Any
from datetime import datetime


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class AdvancedCLI:
    """
    Advanced CLI with structured output and sections
    """

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and self._supports_color()
        self.session_id = None

    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return sys.stdout.isatty() and sys.platform != "win32"

    def set_session(self, session_id: str):
        """Set current session for output"""
        self.session_id = session_id

    def print_header(self, title: str):
        """Print section header"""
        separator = "=" * 60
        self._print_colored(f"\n{separator}", Colors.CYAN)
        self._print_colored(f" {title.upper()} ", Colors.BOLD + Colors.CYAN)
        self._print_colored(f"{separator}\n", Colors.CYAN)

    def print_thought(self, thought: str):
        """Print Jarvis thinking/reasoning"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._print_colored(f"🤔 [{timestamp}] Pensamiento: ", Colors.YELLOW)
        print(thought)

    def print_action(self, action: str, details: Dict[str, Any] = None):
        """Print action being taken"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._print_colored(f"⚡ [{timestamp}] Acción: ", Colors.BLUE)
        print(action)
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    def print_result(self, result: Dict[str, Any]):
        """Print action result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        success = result.get("success", False)

        if success:
            self._print_colored(f"✅ [{timestamp}] Resultado: ", Colors.GREEN)
        else:
            self._print_colored(f"❌ [{timestamp}] Error: ", Colors.RED)

        # Print main result
        if "result" in result:
            print(result["result"])
        elif "error" in result:
            print(result["error"])

        # Print additional info
        for key, value in result.items():
            if key not in ["success", "result", "error"]:
                print(f"   {key}: {value}")

    def print_session_info(self, session_info: Dict[str, Any]):
        """Print session information"""
        self._print_colored("📊 Información de Sesión:", Colors.MAGENTA)
        print(f"   ID: {session_info.get('session_id', 'N/A')}")
        print(f"   Modo: {session_info.get('mode', 'SAFE')}")
        print(f"   Creada: {session_info.get('created_at', 'N/A')}")
        print(f"   Última actividad: {session_info.get('last_activity', 'N/A')}")

    def print_voice_input(self, text: str):
        """Print voice input received"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._print_colored(f"🎤 [{timestamp}] Voz: ", Colors.CYAN)
        print(f'"{text}"')

    def print_system_status(self, status: Dict[str, Any]):
        """Print system status"""
        self._print_colored("🔍 Estado del Sistema:", Colors.WHITE)
        for key, value in status.items():
            print(f"   {key}: {value}")

    def print_proposals_summary(self, summary: Dict[str, Any]):
        """Print improvement proposals summary"""
        self._print_colored("📈 Propuestas de Mejora:", Colors.MAGENTA)
        print(f"   Total: {summary.get('total', 0)}")
        print(f"   Pendientes: {summary.get('pending', 0)}")
        print(f"   Aprobadas: {summary.get('approved', 0)}")
        print(f"   Rechazadas: {summary.get('rejected', 0)}")

        if summary.get('pending', 0) > 0:
            self._print_colored("\n📋 Propuestas Pendientes:", Colors.YELLOW)
            for proposal in summary.get('pending_proposals', []):
                print(f"   • {proposal['id']}: {proposal['title']} ({proposal['priority']})")

    def print_proposal_details(self, proposal: Dict[str, Any]):
        """Print detailed proposal information"""
        self._print_colored(f"📄 Propuesta: {proposal['id']}", Colors.CYAN)
        print(f"   Título: {proposal['title']}")
        print(f"   Tipo: {proposal['type']}")
        print(f"   Prioridad: {proposal['priority']}")
        print(f"   Categoría: {proposal['category']}")
        print(f"   Estado: {proposal['status']}")
        print(f"   Esfuerzo estimado: {proposal['estimated_effort']}")
        print(f"   Nivel de riesgo: {proposal['risk_level']}")
        print(f"   Creada: {proposal['created_at']}")

        print(f"\n   Descripción: {proposal['description']}")

        if proposal.get('proposed_changes'):
            self._print_colored("\n   Cambios Propuestos:", Colors.YELLOW)
            for change in proposal['proposed_changes']:
                print(f"   • {change}")

    def print_learning_insights(self, insights: Dict[str, Any]):
        """Print learning engine insights"""
        self._print_colored("🧠 Insights del Sistema de Aprendizaje:", Colors.CYAN)

        if insights.get('error_patterns'):
            self._print_colored("\n🔍 Patrones de Error Detectados:", Colors.RED)
            for pattern in insights['error_patterns'][:5]:  # Top 5
                print(f"   • {pattern['pattern']}: {pattern['count']} ocurrencias")

        if insights.get('skill_usage'):
            self._print_colored("\n📊 Uso de Skills:", Colors.BLUE)
            for skill in insights['skill_usage'][:5]:  # Top 5
                print(f"   • {skill['skill']}: {skill['usage_count']} usos")

        if insights.get('unknown_intents'):
            self._print_colored("\n❓ Intents Desconocidos:", Colors.YELLOW)
            for intent in insights['unknown_intents'][:5]:  # Top 5
                print(f"   • '{intent['intent']}': {intent['count']} veces")

        if insights.get('improvement_opportunities'):
            self._print_colored("\n💡 Oportunidades de Mejora:", Colors.GREEN)
            for opp in insights['improvement_opportunities'][:3]:  # Top 3
                print(f"   • {opp['title']}: {opp['description']}")

    def print_code_analysis(self, analysis: Dict[str, Any]):
        """Print code analysis results"""
        self._print_colored("🔬 Análisis del Código:", Colors.CYAN)
        print(f"   Archivos totales: {analysis.get('total_files', 0)}")
        print(f"   Líneas totales: {analysis.get('total_lines', 0)}")
        print(f"   Skills registrados: {analysis.get('skills_count', 0)}")

        if analysis.get('languages'):
            self._print_colored("\n   Lenguajes:", Colors.BLUE)
            for lang, count in analysis['languages'].items():
                print(f"   • {lang}: {count} archivos")

        if analysis.get('issues'):
            self._print_colored("\n⚠️  Problemas Detectados:", Colors.YELLOW)
            for issue in analysis['issues']:
                print(f"   • {issue}")

        if analysis.get('security_concerns'):
            security_issues = [issue for issue in analysis['security_concerns'] if "No immediate" not in issue]
            if security_issues:
                self._print_colored("\n🔒 Preocupaciones de Seguridad:", Colors.RED)
                for concern in security_issues:
                    print(f"   • {concern}")

        if analysis.get('recommendations'):
            self._print_colored("\n💡 Recomendaciones:", Colors.GREEN)
            for rec in analysis['recommendations']:
                print(f"   • {rec}")

    def print_separator(self):
        """Print section separator"""
        print("\n" + "-" * 40 + "\n")

    def print_menu(self, options: Dict[str, str]):
        """Print menu options"""
        self._print_colored("📋 Opciones Disponibles:", Colors.BOLD)
        for key, description in options.items():
            print(f"   {key}: {description}")

        # Add auto-improvement commands
        self._print_colored("\n🤖 Comandos de Auto-Mejora:", Colors.CYAN)
        improvement_commands = {
            "analizar": "Analizar codebase y generar propuestas",
            "propuestas": "Ver todas las propuestas de mejora",
            "aprobar <id>": "Aprobar una propuesta específica",
            "rechazar <id>": "Rechazar una propuesta específica",
            "insights": "Ver insights del sistema de aprendizaje",
            "ver <id>": "Ver detalles de una propuesta específica"
        }
        for key, description in improvement_commands.items():
            print(f"   {key}: {description}")

    def _print_colored(self, text: str, color: str):
        """Print colored text if supported"""
        if self.use_colors:
            print(f"{color}{text}{Colors.RESET}", end="")
        else:
            print(text, end="")

    def input_prompt(self, prompt: str = "Jarvis> ") -> str:
        """Get user input with prompt"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            sys.exit(0)
        except EOFError:
            print("\n👋 Fin de entrada")
            sys.exit(0)
