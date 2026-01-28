# skills/what_do_you_know_about_me.py
"""
What Do You Know About Me Skill - User profile and pattern analysis
Provides insights about user habits, preferences, and behavior patterns.
"""

import time
from typing import Dict, Any, List
from collections import Counter


class WhatDoYouKnowAboutMeSkill:
    """
    Skill that analyzes stored data to provide insights about the user.
    Covers habits, technical level, preferences, and behavioral patterns.
    """

    def __init__(self, storage=None, active_learning=None):
        self.storage = storage
        self.active_learning = active_learning

    def run(self, aspect: str = "general") -> Dict[str, Any]:
        """
        Analyze and report what Jarvis knows about the user.

        Args:
            aspect: Specific aspect to focus on ("habits", "technical", "preferences", "general")

        Returns:
            Comprehensive user profile analysis
        """
        try:
            if not self.storage:
                return {
                    "success": False,
                    "error": "No hay almacenamiento disponible para análisis"
                }

            # Get conversation history
            conversations = self.storage.get_last_conversations(200)  # Last 200 interactions

            if not conversations:
                return {
                    "success": False,
                    "error": "No hay suficientes datos de conversación para analizar"
                }

            analysis = {
                "analysis_timestamp": time.time(),
                "total_interactions": len(conversations),
                "analysis_period_days": self._calculate_analysis_period(conversations),
                "user_profile": {}
            }

            # Analyze different aspects
            if aspect == "habits":
                analysis["user_profile"].update(self._analyze_habits(conversations))
            elif aspect == "technical":
                analysis["user_profile"].update(self._analyze_technical_level(conversations))
            elif aspect == "preferences":
                analysis["user_profile"].update(self._analyze_preferences(conversations))
            else:
                # General analysis - all aspects
                analysis["user_profile"].update(self._analyze_habits(conversations))
                analysis["user_profile"].update(self._analyze_technical_level(conversations))
                analysis["user_profile"].update(self._analyze_preferences(conversations))
                analysis["user_profile"].update(self._analyze_behavioral_patterns(conversations))

            # Get current learning insights
            if self.active_learning:
                current_learning = self.active_learning.learn_from_session()
                analysis["current_learning"] = current_learning

            analysis["confidence"] = self._calculate_profile_confidence(analysis)

            return {
                "success": True,
                "aspect": aspect,
                "profile": analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analizando perfil de usuario: {str(e)}",
                "aspect": aspect
            }

    def _calculate_analysis_period(self, conversations: List[Dict[str, Any]]) -> float:
        """Calculate the time period covered by the analysis"""
        if not conversations:
            return 0

        timestamps = []
        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    ts = time.mktime(time.strptime(conv["timestamp"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
                    timestamps.append(ts)
            except:
                continue

        if len(timestamps) < 2:
            return 0

        return (max(timestamps) - min(timestamps)) / (24 * 3600)  # Days

    def _analyze_habits(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user habits and routines"""
        habits = {
            "work_patterns": [],
            "interaction_frequency": {},
            "preferred_times": [],
            "consistency_score": 0
        }

        # Analyze interaction times
        hours = []
        weekdays = []

        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    dt = time.strptime(conv["timestamp"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    hours.append(dt.tm_hour)
                    # tm_wday: 0=Monday, 6=Sunday
                    weekdays.append(dt.tm_wday)
            except:
                continue

        if hours:
            # Most active hours
            hour_counts = Counter(hours)
            peak_hours = [hour for hour, count in hour_counts.most_common(3)]
            habits["preferred_times"] = self._categorize_hours(peak_hours)

            # Work patterns
            if any(9 <= h <= 17 for h in peak_hours):
                habits["work_patterns"].append("horario laboral estándar")
            if any(18 <= h <= 23 for h in peak_hours):
                habits["work_patterns"].append("trabajo nocturno")
            if any(h <= 8 or h >= 22 for h in peak_hours):
                habits["work_patterns"].append("horarios flexibles")

        # Interaction frequency
        if conversations:
            total_days = self._calculate_analysis_period(conversations)
            if total_days > 0:
                daily_avg = len(conversations) / total_days
                habits["interaction_frequency"] = {
                    "daily_average": round(daily_avg, 1),
                    "description": self._categorize_frequency(daily_avg)
                }

        # Consistency score (based on regularity of interactions)
        if len(conversations) > 10:
            habits["consistency_score"] = self._calculate_consistency_score(conversations)

        return {"habits": habits}

    def _analyze_technical_level(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's technical proficiency level"""
        technical = {
            "estimated_level": "principiante",
            "skill_areas": [],
            "learning_indicators": [],
            "confidence": 0.5
        }

        # Analyze command types and complexity
        user_inputs = [conv["user_input"].lower() for conv in conversations]

        # Technical keywords and patterns
        advanced_patterns = [
            "config", "debug", "terminal", "script", "api", "git", "docker",
            "virtualenv", "pip", "requirements", "class", "function", "async"
        ]

        intermediate_patterns = [
            "instalar", "actualizar", "error", "problema", "optimizar",
            "archivo", "carpeta", "buscar", "copiar"
        ]

        basic_patterns = [
            "hora", "fecha", "abrir", "cerrar", "volumen", "brillo"
        ]

        advanced_count = sum(1 for text in user_inputs if any(pat in text for pat in advanced_patterns))
        intermediate_count = sum(1 for text in user_inputs if any(pat in text for pat in intermediate_patterns))
        basic_count = sum(1 for text in user_inputs if any(pat in text for pat in basic_patterns))

        # Determine technical level
        total_technical = advanced_count + intermediate_count + basic_count

        if total_technical == 0:
            technical["estimated_level"] = "desconocido"
        elif advanced_count > intermediate_count and advanced_count > basic_count:
            technical["estimated_level"] = "avanzado"
            technical["skill_areas"] = ["desarrollo", "sistemas", "configuración"]
        elif intermediate_count > basic_count:
            technical["estimated_level"] = "intermedio"
            technical["skill_areas"] = ["uso general", "solución de problemas"]
        else:
            technical["estimated_level"] = "principiante"
            technical["skill_areas"] = ["uso básico", "navegación"]

        # Learning indicators
        learning_keywords = ["aprender", "tutorial", "cómo", "ayuda", "explicar"]
        learning_count = sum(1 for text in user_inputs if any(kw in text for kw in learning_keywords))

        if learning_count > len(conversations) * 0.1:
            technical["learning_indicators"].append("activamente aprendiendo")
        if advanced_count > 0:
            technical["learning_indicators"].append("explorando temas avanzados")

        technical["confidence"] = min(0.9, len(conversations) / 100.0)

        return {"technical_profile": technical}

    def _analyze_preferences(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user preferences and interaction styles"""
        preferences = {
            "interaction_style": [],
            "preferred_topics": [],
            "response_preferences": [],
            "automation_interest": 0
        }

        user_inputs = [conv["user_input"].lower() for conv in conversations]

        # Interaction style analysis
        question_count = sum(1 for text in user_inputs if "?" in text or text.startswith(("cómo", "qué", "cuál", "dónde", "cuándo", "por qué")))
        command_count = sum(1 for text in user_inputs if any(word in text for word in ["abre", "cierra", "busca", "muestra", "haz"]))
        conversation_count = len(user_inputs) - question_count - command_count

        max_style = max(question_count, command_count, conversation_count)
        if question_count == max_style:
            preferences["interaction_style"].append("preguntas y consultas")
        if command_count == max_style:
            preferences["interaction_style"].append("comandos directos")
        if conversation_count == max_style:
            preferences["interaction_style"].append("conversación natural")

        # Preferred topics
        topic_keywords = {
            "sistema": ["cpu", "memoria", "disco", "windows", "linux", "sistema"],
            "productividad": ["archivo", "carpeta", "documento", "trabajo", "escribir"],
            "entretenimiento": ["música", "video", "juego", "película"],
            "comunicación": ["email", "mensaje", "llamar", "contacto"],
            "desarrollo": ["código", "programar", "script", "git", "api"]
        }

        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for text in user_inputs if any(kw in text for kw in keywords))
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            top_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            preferences["preferred_topics"] = [topic for topic, score in top_topics]

        # Automation interest
        automation_keywords = ["automatiz", "siempre", "cada vez", "repetir", "automático"]
        automation_count = sum(1 for text in user_inputs if any(kw in text for kw in automation_keywords))
        preferences["automation_interest"] = min(1.0, automation_count / max(1, len(conversations)))

        return {"preferences": preferences}

    def _analyze_behavioral_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze broader behavioral patterns"""
        patterns = {
            "engagement_level": "bajo",
            "learning_style": [],
            "problem_solving_approach": [],
            "goals_indicators": []
        }

        # Engagement level based on interaction frequency and depth
        total_interactions = len(conversations)
        avg_length = sum(len(conv["user_input"]) for conv in conversations) / max(1, total_interactions)

        if total_interactions > 50 and avg_length > 20:
            patterns["engagement_level"] = "alto"
        elif total_interactions > 20:
            patterns["engagement_level"] = "medio"

        # Learning style indicators
        user_inputs = [conv["user_input"].lower() for conv in conversations]

        if any("explica" in text or "cómo funciona" in text for text in user_inputs):
            patterns["learning_style"].append("prefiere explicaciones detalladas")

        if any("ejemplo" in text or "muestra" in text for text in user_inputs):
            patterns["learning_style"].append("aprende con ejemplos prácticos")

        # Problem solving approach
        if any("intenta" in text or "prueba" in text for text in user_inputs):
            patterns["problem_solving_approach"].append("experimental")

        if any("busca" in text or "encuentra" in text for text in user_inputs):
            patterns["problem_solving_approach"].append("investigativo")

        # Goals indicators
        goal_keywords = ["quiero", "necesito", "objetivo", "meta", "lograr"]
        if any(any(kw in text for kw in goal_keywords) for text in user_inputs):
            patterns["goals_indicators"].append("orientado a objetivos")

        return {"behavioral_patterns": patterns}

    def _categorize_hours(self, hours: List[int]) -> List[str]:
        """Categorize hours into meaningful time periods"""
        categories = []
        for hour in hours:
            if 6 <= hour <= 11:
                categories.append("mañana")
            elif 12 <= hour <= 17:
                categories.append("tarde")
            elif 18 <= hour <= 23:
                categories.append("noche")
            else:
                categories.append("madrugada")
        return list(set(categories))  # Remove duplicates

    def _categorize_frequency(self, daily_avg: float) -> str:
        """Categorize interaction frequency"""
        if daily_avg >= 10:
            return "muy activo"
        elif daily_avg >= 5:
            return "activo"
        elif daily_avg >= 2:
            return "moderado"
        else:
            return "ocasional"

    def _calculate_consistency_score(self, conversations: List[Dict[str, Any]]) -> float:
        """Calculate how consistent user interaction patterns are"""
        if len(conversations) < 10:
            return 0.0

        # Group by day and count interactions per day
        daily_counts = {}
        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    date = conv["timestamp"].split("T")[0]
                    daily_counts[date] = daily_counts.get(date, 0) + 1
            except:
                continue

        if len(daily_counts) < 3:
            return 0.0

        counts = list(daily_counts.values())
        avg_count = sum(counts) / len(counts)
        variance = sum((count - avg_count) ** 2 for count in counts) / len(counts)
        std_dev = variance ** 0.5

        # Lower standard deviation = more consistent
        consistency = max(0, 1 - (std_dev / max(avg_count, 1)))
        return round(consistency, 2)

    def _calculate_profile_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in the profile analysis"""
        factors = []

        # Data quantity factor
        total_interactions = analysis.get("total_interactions", 0)
        quantity_factor = min(1.0, total_interactions / 100.0)
        factors.append(quantity_factor)

        # Time period factor
        period_days = analysis.get("analysis_period_days", 0)
        period_factor = min(1.0, period_days / 30.0)  # Max confidence after 30 days
        factors.append(period_factor)

        # Profile completeness factor
        profile = analysis.get("user_profile", {})
        completeness = len(profile) / 4.0  # 4 main profile sections
        factors.append(completeness)

        return round(sum(factors) / len(factors), 2)