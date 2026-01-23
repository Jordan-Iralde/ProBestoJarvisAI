# skills/evaluate_user_session.py
"""
Evaluate User Session Skill - Session analysis and coaching
Analyzes completed sessions and provides insights, achievements, and improvement suggestions.
"""

import time
from typing import Dict, Any, List
from collections import Counter


class EvaluateUserSessionSkill:
    """
    Skill for evaluating user sessions, providing coaching and improvement insights.
    Analyzes what was done, what was achieved, what was lost, and how to improve next time.
    """

    def __init__(self, storage=None, active_learning=None):
        self.storage = storage
        self.active_learning = active_learning

    def run(self, session_start_time: float = None) -> Dict[str, Any]:
        """
        Evaluate the current or specified user session.

        Args:
            session_start_time: Start time of session to evaluate (uses last 24h if None)

        Returns:
            Comprehensive session evaluation with coaching insights
        """
        try:
            if not self.storage:
                return {
                    "success": False,
                    "error": "No hay almacenamiento disponible para evaluación"
                }

            # Get session conversations
            if session_start_time:
                conversations = self.storage.get_conversations_since(session_start_time)
            else:
                # Default to last 24 hours
                since_time = time.time() - (24 * 3600)
                conversations = self.storage.get_conversations_since(since_time)

            if not conversations:
                return {
                    "success": False,
                    "error": "No hay datos de sesión para evaluar"
                }

            evaluation = {
                "session_info": {
                    "start_time": session_start_time or (time.time() - 24*3600),
                    "end_time": time.time(),
                    "duration_hours": (time.time() - (session_start_time or (time.time() - 24*3600))) / 3600,
                    "total_interactions": len(conversations)
                },
                "what_was_done": [],
                "what_was_achieved": [],
                "what_was_lost": [],
                "how_to_improve": [],
                "session_score": 0,
                "coaching_tips": []
            }

            # Analyze what was done
            evaluation["what_was_done"] = self._analyze_what_was_done(conversations)

            # Analyze achievements
            evaluation["what_was_achieved"] = self._analyze_achievements(conversations)

            # Analyze losses/missed opportunities
            evaluation["what_was_lost"] = self._analyze_losses(conversations)

            # Generate improvement suggestions
            evaluation["how_to_improve"] = self._analyze_improvements(conversations)

            # Calculate session score
            evaluation["session_score"] = self._calculate_session_score(evaluation)

            # Generate coaching tips
            evaluation["coaching_tips"] = self._generate_coaching_tips(evaluation)

            # Add learning insights if available
            if self.active_learning:
                learning = self.active_learning.learn_from_session(session_start_time)
                evaluation["learning_insights"] = learning

            return {
                "success": True,
                "evaluation": evaluation
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error evaluando sesión: {str(e)}"
            }

    def _analyze_what_was_done(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Analyze what activities were performed during the session"""
        activities = []

        # Categorize interactions
        skill_interactions = [conv for conv in conversations if conv["source"] == "skill"]
        llm_interactions = [conv for conv in conversations if conv["source"] == "llm"]
        unknown_interactions = [conv for conv in conversations if conv["source"] == "unknown"]

        # Analyze skill usage
        if skill_interactions:
            skill_inputs = [conv["user_input"].lower() for conv in skill_interactions]
            skill_categories = self._categorize_skill_usage(skill_inputs)

            for category, count in Counter(skill_categories).most_common():
                if count > 1:
                    activities.append(f"Uso intensivo de skills de {category} ({count} veces)")
                else:
                    activities.append(f"Uso de skills de {category}")

        # Analyze conversation topics
        user_inputs = [conv["user_input"].lower() for conv in conversations]

        # Detect specific activities
        if any("escribir" in text or "nota" in text or "anotar" in text for text in user_inputs):
            activities.append("Creación y gestión de notas")

        if any("buscar" in text or "encontrar" in text or "archivo" in text for text in user_inputs):
            activities.append("Búsqueda y localización de archivos")

        if any("abrir" in text or "cerrar" in text or "app" in text for text in user_inputs):
            activities.append("Gestión de aplicaciones")

        if any("hora" in text or "fecha" in text or "tiempo" in text for text in user_inputs):
            activities.append("Consultas de tiempo y calendario")

        if any("sistema" in text or "cpu" in text or "memoria" in text for text in user_inputs):
            activities.append("Monitoreo del sistema")

        # Analyze conversation patterns
        if len(llm_interactions) > len(skill_interactions) * 2:
            activities.append("Sesión conversacional intensa")
        elif len(unknown_interactions) > len(conversations) * 0.3:
            activities.append("Exploración y aprendizaje de nuevas funcionalidades")

        # Time-based analysis
        if len(conversations) > 20:
            activities.append("Sesión prolongada y productiva")
        elif len(conversations) < 5:
            activities.append("Sesión breve")

        return activities[:8]  # Limit to top activities

    def _analyze_achievements(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Analyze what was achieved during the session"""
        achievements = []

        # Success indicators
        successful_skills = sum(1 for conv in conversations
                              if conv["source"] == "skill" and len(conv["response"]) > 10)

        if successful_skills > 0:
            achievements.append(f"Ejecución exitosa de {successful_skills} skills")

        # Learning achievements
        user_inputs = [conv["user_input"].lower() for conv in conversations]

        learning_indicators = sum(1 for text in user_inputs
                                if any(word in text for word in ["aprender", "tutorial", "cómo", "explicar"]))

        if learning_indicators > 0:
            achievements.append(f"Actividad de aprendizaje detectada ({learning_indicators} consultas)")

        # Productivity achievements
        productivity_indicators = sum(1 for text in user_inputs
                                    if any(word in text for word in ["organizar", "optimizar", "mejorar", "completar"]))

        if productivity_indicators > 0:
            achievements.append(f"Actividades productivas realizadas ({productivity_indicators} acciones)")

        # Problem solving achievements
        problem_solving = sum(1 for conv in conversations
                            if "error" in conv["user_input"].lower() or "problema" in conv["user_input"].lower())

        if problem_solving > 0:
            achievements.append(f"Resolución de problemas técnicos ({problem_solving} consultas)")

        # Exploration achievements
        unique_inputs = len(set(conv["user_input"] for conv in conversations))
        diversity_ratio = unique_inputs / len(conversations) if conversations else 0

        if diversity_ratio > 0.8:
            achievements.append("Exploración diversa de funcionalidades")
        elif diversity_ratio > 0.6:
            achievements.append("Buen equilibrio entre diferentes tipos de tareas")

        # Session continuity
        if len(conversations) >= 10:
            achievements.append("Sesión consistente y enfocada")

        return achievements

    def _analyze_losses(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Analyze what was lost or missed during the session"""
        losses = []

        # Unknown intents (missed opportunities)
        unknown_count = sum(1 for conv in conversations if conv["source"] == "unknown")
        if unknown_count > 0:
            losses.append(f"{unknown_count} interacciones no comprendidas completamente")

        # Repetitive queries (inefficiency)
        user_inputs = [conv["user_input"].lower() for conv in conversations]
        input_counts = Counter(user_inputs)
        repetitive_queries = sum(1 for count in input_counts.values() if count > 1)

        if repetitive_queries > 0:
            losses.append(f"{repetitive_queries} consultas repetidas (posible ineficiencia)")

        # Short responses (possibly incomplete interactions)
        short_responses = sum(1 for conv in conversations if len(conv["response"]) < 20)
        if short_responses > len(conversations) * 0.3:
            losses.append("Varias respuestas cortas sugieren interacciones incompletas")

        # Time gaps (lost focus)
        timestamps = []
        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    ts = time.mktime(time.strptime(conv["timestamp"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
                    timestamps.append(ts)
            except:
                continue

        if len(timestamps) > 5:
            gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            large_gaps = sum(1 for gap in gaps if gap > 1800)  # 30 minutes
            if large_gaps > 0:
                losses.append(f"{large_gaps} periodos largos de inactividad")

        # Missed automation opportunities
        automation_keywords = ["siempre", "cada vez", "repetir", "automático"]
        automation_mentions = sum(1 for text in user_inputs
                                if any(kw in text for kw in automation_keywords))

        if automation_mentions > 0:
            losses.append("Oportunidades de automatización no aprovechadas")

        # Unexplored features
        total_interactions = len(conversations)
        skill_usage = len([conv for conv in conversations if conv["source"] == "skill"])

        if total_interactions > 10 and skill_usage < 3:
            losses.append("Bajo aprovechamiento de skills disponibles")

        return losses

    def _analyze_improvements(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Generate suggestions for how to improve future sessions"""
        improvements = []

        # Based on unknown intents
        unknown_rate = sum(1 for conv in conversations if conv["source"] == "unknown") / len(conversations) if conversations else 0

        if unknown_rate > 0.3:
            improvements.append("Mejorar formulación de consultas para mayor comprensión")
            improvements.append("Explorar más skills disponibles para cubrir necesidades")

        # Based on interaction patterns
        user_inputs = [conv["user_input"].lower() for conv in conversations]
        avg_input_length = sum(len(text) for text in user_inputs) / len(user_inputs) if user_inputs else 0

        if avg_input_length < 10:
            improvements.append("Usar consultas más específicas y detalladas")

        # Based on session length
        if len(conversations) > 30:
            improvements.append("Considerar breaks en sesiones muy largas para mantener foco")
        elif len(conversations) < 5:
            improvements.append("Explorar más funcionalidades para enriquecer las sesiones")

        # Based on skill diversity
        skill_conversations = [conv for conv in conversations if conv["source"] == "skill"]
        if skill_conversations:
            skill_types = self._categorize_skill_usage([conv["user_input"] for conv in skill_conversations])
            unique_skills = len(set(skill_types))

            if unique_skills < 3 and len(skill_conversations) > 5:
                improvements.append("Diversificar el uso de diferentes tipos de skills")

        # Based on time efficiency
        if conversations:
            session_duration = (time.time() - time.mktime(time.strptime(conversations[0]["timestamp"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))) / 3600 if conversations[0]["timestamp"] else 0
            interactions_per_hour = len(conversations) / max(session_duration, 1)

            if interactions_per_hour > 10:
                improvements.append("Mejorar eficiencia - demasiadas interacciones por hora")
            elif interactions_per_hour < 2:
                improvements.append("Aumentar engagement - pocas interacciones por hora")

        # Learning suggestions
        reflection_indicators = sum(1 for text in user_inputs
                                  if any(word in text for word in ["resum", "analiz", "valor", "sesion"]))

        if reflection_indicators == 0 and len(conversations) > 10:
            improvements.append("Incluir más análisis reflexivo al final de sesiones")

        return improvements[:6]  # Limit to top improvements

    def _categorize_skill_usage(self, user_inputs: List[str]) -> List[str]:
        """Categorize skill usage patterns"""
        categories = []
        for input_text in user_inputs:
            text = input_text.lower()
            if any(word in text for word in ["hora", "time", "fecha"]):
                categories.append("tiempo")
            elif any(word in text for word in ["abrir", "abre", "open", "cerrar"]):
                categories.append("aplicaciones")
            elif any(word in text for word in ["estado", "status", "cpu", "memoria", "sistema"]):
                categories.append("sistema")
            elif any(word in text for word in ["nota", "anota", "note", "escribir"]):
                categories.append("productividad")
            elif any(word in text for word in ["busca", "encuentra", "search", "archivo"]):
                categories.append("búsqueda")
            else:
                categories.append("otros")
        return categories

    def _calculate_session_score(self, evaluation: Dict[str, Any]) -> float:
        """Calculate overall session score (0-100)"""
        score = 50  # Base score

        # Achievements boost score
        achievements = len(evaluation.get("what_was_achieved", []))
        score += min(20, achievements * 3)

        # Losses reduce score
        losses = len(evaluation.get("what_was_lost", []))
        score -= min(15, losses * 2)

        # Interaction quality
        total_interactions = evaluation.get("session_info", {}).get("total_interactions", 0)
        if total_interactions > 20:
            score += 10
        elif total_interactions < 5:
            score -= 10

        # Diversity bonus
        what_done = evaluation.get("what_was_done", [])
        if len(what_done) >= 3:
            score += 5

        return max(0, min(100, score))

    def _generate_coaching_tips(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate personalized coaching tips based on evaluation"""
        tips = []

        session_score = evaluation.get("session_score", 50)

        if session_score >= 80:
            tips.append("¡Excelente sesión! Mantén este nivel de productividad")
        elif session_score >= 60:
            tips.append("Buena sesión. Pequeñas optimizaciones pueden llevarte al siguiente nivel")
        else:
            tips.append("Sesión con oportunidades de mejora. Enfócate en ser más específico en tus consultas")

        # Specific coaching based on analysis
        achievements = evaluation.get("what_was_achieved", [])
        losses = evaluation.get("what_was_lost", [])

        if any("aprendizaje" in achievement.lower() for achievement in achievements):
            tips.append("Tu enfoque en el aprendizaje es admirable. Considera documentar lo aprendido")

        if any("repetidas" in loss.lower() for loss in losses):
            tips.append("Reduce consultas repetidas aprendiendo atajos o creando automatizaciones")

        if len(achievements) > len(losses) * 2:
            tips.append("¡Sesión muy productiva! Identifica qué funcionó bien para replicarlo")
        elif len(losses) > len(achievements):
            tips.append("Enfócate en maximizar logros y minimizar pérdidas en futuras sesiones")

        return tips[:4]  # Limit to top coaching tips