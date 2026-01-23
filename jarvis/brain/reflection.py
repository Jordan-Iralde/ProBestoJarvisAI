# brain/reflection.py
"""
Reflection Module - Passive analysis for insights and suggestions
No modifications, only observations and insights generation.
"""

import time
from typing import List, Dict, Any
from collections import Counter


class ReflectionAnalyzer:
    """
    Passive reflection analyzer that generates insights from usage patterns.
    Never modifies system state, only observes and suggests.
    """

    def __init__(self, storage, logger=None):
        self.storage = storage
        self.logger = logger

    def analyze_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Analyze recent activity patterns and generate insights.
        """
        insights = []
        since_time = time.time() - (hours * 3600)

        conversations = self.storage.get_conversations_since(since_time)

        if not conversations:
            return [{"insight": "No hay actividad reciente para analizar", "type": "info"}]

        # Análisis básico
        total_interactions = len(conversations)
        sources = Counter(conv["source"] for conv in conversations)
        intents = self._extract_intents_from_conversations(conversations)

        # Insight 1: Patrón de uso
        if sources.get("skill", 0) > sources.get("llm", 0) * 2:
            insights.append({
                "insight": f"Usuario prefiere comandos determinísticos ({sources['skill']} skills vs {sources.get('llm', 0)} LLM)",
                "suggestion": "Considerar agregar más skills para tareas comunes",
                "type": "usage_pattern"
            })

        # Insight 2: Skills más usadas
        skill_usage = Counter(intent for intent, source in intents.items() if source == "skill")
        if skill_usage:
            most_used = skill_usage.most_common(1)[0]
            if most_used[1] >= 3:
                insights.append({
                    "insight": f"Skill '{most_used[0]}' usado {most_used[1]} veces recientemente",
                    "suggestion": "Crear acceso rápido o alias para esta skill",
                    "type": "frequent_skill"
                })

        # Insight 3: Intents fallidos
        unknown_count = sources.get("unknown", 0)
        if unknown_count > total_interactions * 0.3:
            insights.append({
                "insight": f"Alta tasa de intents desconocidos ({unknown_count}/{total_interactions})",
                "suggestion": "Mejorar NLU con más patterns o soft matching",
                "type": "unknown_intents"
            })

        # Insight 4: Sesiones largas
        if total_interactions > 10:
            insights.append({
                "insight": f"Sesión activa con {total_interactions} interacciones",
                "suggestion": "Ofrecer resumen automático al final de sesiones largas",
                "type": "session_length"
            })

        # Insight 5: Diversidad de interacciones
        unique_intents = len(set(intents.keys()))
        if unique_intents >= 5:
            insights.append({
                "insight": f"Usuario explora {unique_intents} diferentes tipos de comandos",
                "suggestion": "Sistema se adapta bien a diferentes necesidades",
                "type": "exploration"
            })

        return insights if insights else [{"insight": "Actividad normal detectada", "type": "neutral"}]

    def _extract_intents_from_conversations(self, conversations: List[Dict]) -> Dict[str, str]:
        """
        Extrae intents aproximados de conversaciones.
        Como no tenemos intents guardados, infiere de user_input.
        """
        intents = {}

        for conv in conversations:
            user_input = conv["user_input"].lower()
            source = conv["source"]

            # Inferir intent de user_input (simple)
            if "hora" in user_input or "time" in user_input:
                intents["get_time"] = source
            elif "abrir" in user_input or "open" in user_input:
                intents["open_app"] = source
            elif "estado" in user_input or "status" in user_input:
                intents["system_status"] = source
            elif "nota" in user_input or "note" in user_input:
                intents["create_note"] = source
            elif "busca" in user_input or "search" in user_input:
                intents["search_file"] = source
            elif "resum" in user_input or "actividad" in user_input:
                intents["summarize_recent_activity"] = source
            else:
                intents["unknown"] = source

        return intents

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Estadísticas generales de uso.
        """
        # Obtener últimas 100 conversaciones
        conversations = self.storage.get_last_conversations(100)

        if not conversations:
            return {"total_conversations": 0}

        sources = Counter(conv["source"] for conv in conversations)
        intents = self._extract_intents_from_conversations(conversations)

        return {
            "total_conversations": len(conversations),
            "sources_distribution": dict(sources),
            "intents_distribution": dict(Counter(intents.values())),
            "most_common_intent": Counter(intents.keys()).most_common(1)[0] if intents else None
        }