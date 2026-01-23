# brain/reflection_engine.py
"""
Active Learning Engine - Observes, learns and proposes improvements
No modifications, only observations and structured learning insights.
"""

import time
from typing import List, Dict, Any, Optional
from collections import Counter


class ActiveLearningEngine:
    """
    Active learning engine that analyzes usage patterns and generates learning insights.
    Never modifies system state, only observes and provides structured learning feedback.
    """

    def __init__(self, storage, nlu_parser=None, logger=None):
        self.storage = storage
        self.nlu_parser = nlu_parser
        self.logger = logger

    def learn_from_session(self, session_start_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Active learning from session data.
        Returns structured learning insights about user patterns and improvement opportunities.
        """
        if session_start_time is None:
            # Analyze last 24 hours if no session time
            since_time = time.time() - (24 * 3600)
            conversations = self.storage.get_conversations_since(since_time)
        else:
            conversations = self.storage.get_conversations_since(session_start_time)

        if not conversations:
            return {
                "user_patterns": [],
                "skill_gaps": [],
                "learning_targets": ["Necesita más datos para aprender"],
                "confidence": 0.0
            }

        # Analyze user patterns
        user_patterns = self._analyze_user_patterns(conversations)

        # Analyze skill gaps
        skill_gaps = self._analyze_skill_gaps(conversations)

        # Analyze learning targets
        learning_targets = self._analyze_learning_targets(conversations)

        # Calculate confidence based on data quality and quantity
        confidence = self._calculate_learning_confidence(conversations)

        return {
            "user_patterns": user_patterns,
            "skill_gaps": skill_gaps,
            "learning_targets": learning_targets,
            "confidence": round(confidence, 2)
        }

    def analyze_session(self, session_start_time: Optional[float] = None) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        Use learn_from_session() for new structured learning output.
        """
        learning = self.learn_from_session(session_start_time)
        return {
            "session_insights": learning["user_patterns"] + learning["learning_targets"],
            "opportunity_signals": learning["skill_gaps"],
            "confidence": learning["confidence"]
        }

    def _analyze_user_patterns(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Analyze user behavior patterns"""
        patterns = []

        # Analyze time patterns
        hours = []
        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    hour = int(conv["timestamp"].split("T")[1].split(":")[0])
                    hours.append(hour)
            except:
                continue

        if hours:
            most_active_hour = Counter(hours).most_common(1)[0][0]
            if 9 <= most_active_hour <= 17:
                patterns.append("trabajo diurno")
            elif 18 <= most_active_hour <= 23:
                patterns.append("trabajo nocturno")
            elif 0 <= most_active_hour <= 8:
                patterns.append("trabajo temprano")

        # Analyze interaction types
        sources = [conv["source"] for conv in conversations]
        skill_count = sources.count("skill")
        llm_count = sources.count("llm")
        unknown_count = sources.count("unknown")

        total = len(conversations)
        if skill_count > total * 0.6:
            patterns.append("preferencia por comandos específicos")
        if llm_count > total * 0.6:
            patterns.append("preferencia por conversación natural")
        if unknown_count > total * 0.3:
            patterns.append("exploración y aprendizaje")

        # Analyze reflection interest
        reflection_keywords = ["analiz", "resum", "valor", "sesion", "reflexion"]
        reflection_count = sum(1 for conv in conversations
                             if any(kw in conv["user_input"].lower() for kw in reflection_keywords))

        if reflection_count >= 3:
            patterns.append("reflexión y metaanálisis")
        elif reflection_count >= 1:
            patterns.append("interés en auto-evaluación")

        # Analyze technical depth
        technical_keywords = ["config", "error", "debug", "optimiz", "sistema"]
        technical_count = sum(1 for conv in conversations
                            if any(kw in conv["user_input"].lower() for kw in technical_keywords))

        if technical_count >= 5:
            patterns.append("trabajo técnico avanzado")
        elif technical_count >= 2:
            patterns.append("interés técnico moderado")

        return patterns[:5]  # Limit to top 5 patterns

    def _analyze_skill_gaps(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Identify gaps in available skills"""
        gaps = []

        # Check for repeated unknown intents
        sources = [conv["source"] for conv in conversations]
        unknown_rate = sources.count("unknown") / len(conversations) if conversations else 0

        if unknown_rate > 0.4:
            gaps.append("mejorar reconocimiento de intents naturales")

        # Check for system-related queries without system skills
        system_queries = sum(1 for conv in conversations
                           if any(word in conv["user_input"].lower()
                                for word in ["cpu", "memoria", "disco", "rendimiento", "optimiz"]))

        if system_queries >= 3 and sources.count("skill") < system_queries * 0.5:
            gaps.append("skills de monitoreo y optimización del sistema")

        # Check for reflection/analysis queries
        reflection_queries = sum(1 for conv in conversations
                               if any(word in conv["user_input"].lower()
                                    for word in ["analiz", "resum", "valor", "sesion"]))

        if reflection_queries >= 2:
            gaps.append("skills de análisis y resumen ejecutivo")

        # Check for automation interest
        automation_keywords = ["automatiz", "repetir", "siempre", "cada vez"]
        automation_interest = sum(1 for conv in conversations
                                if any(kw in conv["user_input"].lower() for kw in automation_keywords))

        if automation_interest >= 2:
            gaps.append("automatización de tareas repetitivas")

        return gaps[:4]  # Limit to top 4 gaps

    def _analyze_learning_targets(self, conversations: List[Dict[str, Any]]) -> List[str]:
        """Identify what the system should learn"""
        targets = []

        # Analyze frustration patterns (reformulations)
        user_inputs = [conv["user_input"] for conv in conversations]
        unique_inputs = len(set(user_inputs))

        if len(conversations) > 10 and unique_inputs / len(conversations) < 0.7:
            targets.append("mejorar comprensión de consultas reformuladas")

        # Analyze time between interactions
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
            avg_gap = sum(gaps) / len(gaps)
            if avg_gap > 300:  # 5 minutes
                targets.append("reducir tiempo de respuesta para mantener flujo")

        # Analyze NLU performance
        unknown_count = sum(1 for conv in conversations if conv["source"] == "unknown")
        if unknown_count > len(conversations) * 0.2:
            targets.append("expandir vocabulario y patrones de NLU")

        # Analyze skill diversity
        skill_conversations = [conv for conv in conversations if conv["source"] == "skill"]
        if len(skill_conversations) > 0:
            skill_types = self._classify_skill_usage([conv["user_input"] for conv in skill_conversations])
            unique_skills = len(set(skill_types))
            if unique_skills < 3 and len(skill_conversations) > 10:
                targets.append("diversificar conjunto de skills disponibles")

        return targets[:3]  # Limit to top 3 targets

    def _calculate_learning_confidence(self, conversations: List[Dict[str, Any]]) -> float:
        """Calculate confidence in learning insights"""
        if not conversations:
            return 0.0

        # Base confidence on data quantity
        quantity_score = min(1.0, len(conversations) / 50.0)

        # Quality factors
        quality_factors = []

        # Diversity of interactions
        sources = [conv["source"] for conv in conversations]
        unique_sources = len(set(sources))
        quality_factors.append(unique_sources / 3.0)  # Max 3 sources

        # Time span coverage
        timestamps = []
        for conv in conversations:
            try:
                if "T" in conv["timestamp"]:
                    ts = time.mktime(time.strptime(conv["timestamp"].split(".")[0], "%Y-%m-%dT%H:%M:%S"))
                    timestamps.append(ts)
            except:
                continue

        if len(timestamps) > 1:
            time_span = max(timestamps) - min(timestamps)
            time_coverage = min(1.0, time_span / 3600.0)  # Max 1 hour
            quality_factors.append(time_coverage)

        # Average quality
        avg_quality = sum(quality_factors) / len(quality_factors) if quality_factors else 0.5

        return min(0.95, quantity_score * avg_quality)
        skill_analysis = self._analyze_skill_usage(conversations)
        insights.extend(skill_analysis["insights"])
        opportunities.extend(skill_analysis["opportunities"])

        # Análisis de patrones conversacionales
        conversation_analysis = self._analyze_conversation_patterns(conversations)
        insights.extend(conversation_analysis["insights"])
        opportunities.extend(conversation_analysis["opportunities"])

        # Calcular confianza basada en cantidad de datos
        confidence = min(0.95, len(conversations) / 20.0)

        return {
            "session_insights": insights,
            "opportunity_signals": opportunities,
            "confidence": round(confidence, 2),
            "analyzed_interactions": len(conversations)
        }

    def _analyze_intent_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze patterns in intent recognition"""
        insights = []
        opportunities = []

        sources = [conv["source"] for conv in conversations]
        unknown_count = sources.count("unknown")
        total_count = len(conversations)

        unknown_rate = unknown_count / total_count if total_count > 0 else 0

        if unknown_rate > 0.4:
            insights.append(f"Tasa alta de intents desconocidos ({unknown_count}/{total_count})")
            opportunities.append("Mejorar NLU con más patterns o soft matching para frases conversacionales")
        elif unknown_rate < 0.1:
            insights.append("Excelente reconocimiento de intents")
            opportunities.append("Sistema maduro, considerar expansión de vocabulario")

        # Detectar patrones de fallback
        if unknown_count > 0:
            insights.append(f"{unknown_count} interacciones cayeron en respuestas genéricas")
            opportunities.append("Implementar respuestas más contextuales para unknowns")

        return {"insights": insights, "opportunities": opportunities}

    def _analyze_skill_usage(self, conversations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze which skills are used and how"""
        insights = []
        opportunities = []

        skill_conversations = [conv for conv in conversations if conv["source"] == "skill"]
        llm_conversations = [conv for conv in conversations if conv["source"] == "llm"]

        skill_count = len(skill_conversations)
        llm_count = len(llm_conversations)

        if skill_count > llm_count * 2:
            insights.append(f"Uso predominante de skills ({skill_count} vs {llm_count} LLM)")
            opportunities.append("Usuario cómodo con comandos, considerar más automatización")
        elif llm_count > skill_count * 2:
            insights.append(f"Uso predominante de conversación ({llm_count} vs {skill_count} skills)")
            opportunities.append("Usuario prefiere diálogo, mejorar capacidades conversacionales")

        # Skills más usadas
        skill_inputs = [conv["user_input"] for conv in skill_conversations]
        skill_types = self._classify_skill_usage(skill_inputs)

        most_common = Counter(skill_types).most_common(1)
        if most_common:
            skill_name, count = most_common[0]
            if count >= 3:
                insights.append(f"Skill '{skill_name}' usado {count} veces")
                opportunities.append(f"Crear acceso rápido o alias para '{skill_name}'")

        return {"insights": insights, "opportunities": opportunities}

    def _analyze_conversation_patterns(self, conversations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze conversation flow and patterns"""
        insights = []
        opportunities = []

        # Longitud de sesión
        if len(conversations) >= 10:
            insights.append("Sesión prolongada detectada")
            opportunities.append("Implementar resúmenes automáticos en sesiones largas")

        # Diversidad de interacciones
        user_inputs = [conv["user_input"] for conv in conversations]
        unique_inputs = len(set(user_inputs))

        diversity_ratio = unique_inputs / len(conversations) if conversations else 0

        if diversity_ratio < 0.5:
            insights.append("Repetición frecuente de consultas similares")
            opportunities.append("Mejorar retención de contexto o sugerir variaciones")

        # Detección de reflexión
        reflection_keywords = ["resum", "analiz", "valor", "sesion", "actividad"]
        reflection_count = sum(1 for conv in conversations
                             if any(kw in conv["user_input"].lower() for kw in reflection_keywords))

        if reflection_count >= 2:
            insights.append(f"Usuario mostró interés en reflexión/metaanálisis ({reflection_count} veces)")
            opportunities.append("Nueva skill sugerida: analyze_session_value o explain_recent_decisions")

        return {"insights": insights, "opportunities": opportunities}

    def _classify_skill_usage(self, user_inputs: List[str]) -> List[str]:
        """Clasifica el tipo de skill usado basado en input"""
        classifications = []
        for input_text in user_inputs:
            text = input_text.lower()
            if any(word in text for word in ["hora", "time", "fecha"]):
                classifications.append("get_time")
            elif any(word in text for word in ["abrir", "abre", "open"]):
                classifications.append("open_app")
            elif any(word in text for word in ["estado", "status", "cpu"]):
                classifications.append("system_status")
            elif any(word in text for word in ["nota", "anota", "note"]):
                classifications.append("create_note")
            elif any(word in text for word in ["busca", "encuentra", "search"]):
                classifications.append("search_file")
            elif any(word in text for word in ["resum", "actividad"]):
                classifications.append("summarize")
            else:
                classifications.append("other_skill")
        return classifications

    def get_usage_stats(self) -> Dict[str, Any]:
        """General usage statistics"""
        conversations = self.storage.get_last_conversations(100)

        if not conversations:
            return {"total_sessions": 0}

        # Agrupar por sesiones (simplificado: sesiones separadas por gaps > 30 min)
        sessions = self._group_into_sessions(conversations)

        return {
            "total_interactions": len(conversations),
            "estimated_sessions": len(sessions),
            "avg_session_length": round(len(conversations) / max(len(sessions), 1), 1),
            "most_active_period": self._get_most_active_period(conversations)
        }

    def _group_into_sessions(self, conversations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group conversations into sessions based on time gaps"""
        if not conversations:
            return []

        import time
        sessions = []
        current_session = [conversations[0]]

        for conv in conversations[1:]:
            try:
                # Parse timestamp - handle different formats
                prev_timestamp = current_session[-1]["timestamp"]
                curr_timestamp = conv["timestamp"]

                # Convert ISO format to timestamp
                if "T" in prev_timestamp:
                    prev_time = time.mktime(time.strptime(prev_timestamp.split(".")[0], "%Y-%m-%dT%H:%M:%S"))
                else:
                    prev_time = float(prev_timestamp)

                if "T" in curr_timestamp:
                    curr_time = time.mktime(time.strptime(curr_timestamp.split(".")[0], "%Y-%m-%dT%H:%M:%S"))
                else:
                    curr_time = float(curr_timestamp)

                if curr_time - prev_time > 1800:  # 30 minutes
                    sessions.append(current_session)
                    current_session = [conv]
                else:
                    current_session.append(conv)
            except (ValueError, KeyError):
                # If parsing fails, treat as same session
                current_session.append(conv)

        if current_session:
            sessions.append(current_session)

        return sessions

    def _get_most_active_period(self, conversations: List[Dict[str, Any]]) -> str:
        """Determine most active time period"""
        if not conversations:
            return "N/A"

        # Simplificado: contar por hora del día
        hours = []
        for conv in conversations:
            try:
                # Extraer hora del timestamp ISO
                timestamp = conv["timestamp"]
                if "T" in timestamp:
                    hour = int(timestamp.split("T")[1].split(":")[0])
                else:
                    # Si no es ISO, asumir que es timestamp y convertir
                    import time
                    hour = time.localtime(float(timestamp)).tm_hour
                hours.append(hour)
            except:
                continue

        if hours:
            most_common_hour = Counter(hours).most_common(1)[0][0]
            return f"{most_common_hour:02d}:00 - {most_common_hour+1:02d}:00"
        return "N/A"