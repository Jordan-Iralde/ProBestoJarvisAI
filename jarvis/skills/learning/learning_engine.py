# skills/learning_engine.py
"""
Learning & Insight Engine for JarvisAI v0.0.4
Analyzes sessions, errors, and unknown intents to generate insights
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict


class LearningEngineSkill:
    """
    Learning & Insight Engine
    Analyzes JarvisAI's behavior to generate insights and improvement opportunities
    """

    patterns = [
        r"\b(analizar|analyze|aprender|learn|insights|mejoras|improvements)\b.*\b(sesion|sesión|session|errores|errors|unknown)\b",
        r"\b(que puedo mejorar|what can i improve|learning|insights)\b",
        r"\b(evaluar|evaluate|analizar|analyze)\b.*\b(rendimiento|performance|sesiones|sessions)\b"
    ]

    def run(self, entities, core):
        """Generate insights from JarvisAI's operation data"""

        # Analyze different aspects
        insights = {
            "session_analysis": self._analyze_sessions(core),
            "error_analysis": self._analyze_errors(core),
            "unknown_intents": self._analyze_unknown_intents(core),
            "skill_usage": self._analyze_skill_usage(core),
            "performance_metrics": self._analyze_performance(core),
            "improvement_opportunities": self._generate_improvement_opportunities(core)
        }

        # Save insights for future reference
        self._save_insights(core, insights)

        # Format response
        response = self._format_insights_response(insights)

        return {
            "success": True,
            "result": response,
            "insights": insights
        }

    def _analyze_sessions(self, core) -> Dict[str, Any]:
        """Analyze session patterns and duration"""
        sessions = core.session_manager.list_all_sessions()
        if not sessions:
            return {"total_sessions": 0, "insights": []}

        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.get('active', False)])

        # Calculate session durations
        durations = []
        for session in sessions:
            if session.get('created_at') and session.get('last_activity'):
                try:
                    created = datetime.fromisoformat(session['created_at'])
                    last_activity = datetime.fromisoformat(session['last_activity'])
                    duration = (last_activity - created).total_seconds()
                    durations.append(duration)
                except:
                    pass

        avg_duration = sum(durations) / len(durations) if durations else 0

        insights = []
        if total_sessions > 10:
            insights.append(f"Has tenido {total_sessions} sesiones, promedio de {avg_duration/60:.1f} minutos cada una")
        if active_sessions > 1:
            insights.append(f"Tienes {active_sessions} sesiones activas simultáneamente")

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "avg_duration_minutes": avg_duration / 60,
            "insights": insights
        }

    def _analyze_errors(self, core) -> Dict[str, Any]:
        """Analyze error patterns"""
        # This would need access to error logs
        # For now, return basic structure
        return {
            "total_errors": 0,
            "error_types": {},
            "insights": ["Análisis de errores no implementado aún"]
        }

    def _analyze_unknown_intents(self, core) -> Dict[str, Any]:
        """Analyze unknown intents to identify missing skills"""
        # Get command history from current session
        history = getattr(core, 'command_history', [])

        unknown_commands = []
        for cmd in history[-50:]:  # Last 50 commands
            # This is a simplification - in reality we'd need to check logs
            if any(word in cmd.lower() for word in ['pc', 'cerrar sesion', 'resumir', 'evaluar']):
                unknown_commands.append(cmd)

        insights = []
        if unknown_commands:
            insights.append(f"Detecté {len(unknown_commands)} comandos desconocidos recientemente")
            insights.append("Posibles nuevas skills necesarias: gestión de PC, resumen de sesiones, evaluación")

        return {
            "unknown_commands": unknown_commands,
            "potential_new_skills": ["system_management", "session_summary", "evaluation"],
            "insights": insights
        }

    def _analyze_skill_usage(self, core) -> Dict[str, Any]:
        """Analyze which skills are used most"""
        # This would need access to usage logs
        skills = list(core.skill_dispatcher.skills.keys())
        return {
            "total_skills": len(skills),
            "available_skills": skills,
            "insights": [f"Tienes {len(skills)} skills disponibles"]
        }

    def _analyze_performance(self, core) -> Dict[str, Any]:
        """Analyze performance metrics"""
        return {
            "avg_response_time": 0.5,  # Placeholder
            "success_rate": 0.85,      # Placeholder
            "insights": ["Métricas de rendimiento básicas disponibles"]
        }

    def _generate_improvement_opportunities(self, core) -> List[str]:
        """Generate specific improvement suggestions"""
        opportunities = []

        # Check for missing skills based on unknown commands
        unknown_analysis = self._analyze_unknown_intents(core)
        if unknown_analysis['potential_new_skills']:
            opportunities.append(f"Implementar skills para: {', '.join(unknown_analysis['potential_new_skills'])}")

        # Voice capabilities
        if not core.voice_pipeline.is_voice_available():
            opportunities.append("Mejorar capacidades de voz instalando dependencias faltantes")

        # Session management
        session_analysis = self._analyze_sessions(core)
        if session_analysis['active_sessions'] > 1:
            opportunities.append("Optimizar manejo de múltiples sesiones concurrentes")

        opportunities.extend([
            "Implementar sistema de auto-programación segura",
            "Mejorar interfaz de usuario con más opciones visuales",
            "Agregar capacidad de búsqueda web para consultas complejas",
            "Implementar sistema de propuestas y aprobaciones"
        ])

        return opportunities

    def _save_insights(self, core, insights: Dict[str, Any]):
        """Save insights to disk for future reference"""
        try:
            data_dir = os.path.join(os.path.expanduser("~"), "Desktop", "JarvisData", "insights")
            os.makedirs(data_dir, exist_ok=True)

            filename = os.path.join(data_dir, f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            core.logger.logger.warning(f"Could not save insights: {e}")

    def _format_insights_response(self, insights: Dict[str, Any]) -> str:
        """Format insights into a readable response"""
        response_parts = ["🔍 Análisis de JarvisAI completado:\n"]

        # Session analysis
        session = insights['session_analysis']
        response_parts.append(f"📊 Sesiones: {session['total_sessions']} totales, {session['active_sessions']} activas")

        # Unknown intents
        unknown = insights['unknown_intents']
        if unknown['unknown_commands']:
            response_parts.append(f"❓ Comandos desconocidos recientes: {len(unknown['unknown_commands'])}")

        # Skills
        skills = insights['skill_usage']
        response_parts.append(f"🛠️ Skills disponibles: {skills['total_skills']}")

        # Improvement opportunities
        opportunities = insights['improvement_opportunities']
        if opportunities:
            response_parts.append("\n💡 Oportunidades de mejora:")
            for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                response_parts.append(f"  {i}. {opp}")

        return "\n".join(response_parts)