# skills/analyze_session_value.py
import time
from typing import List, Dict, Any


class AnalyzeSessionValueSkill:
    """Analiza el valor y utilidad de la sesión actual"""

    # Patrones para detección
    patterns = [
        r"valio.*la.*pena.*sesion",
        r"que.*deberia.*hacer.*ahora",
        r"vamos.*bien",
        r"dame.*siguiente.*paso",
        r"analiz.*sesion",
        r"valor.*sesion",
        r"que.*aprendi",
        r"resumen.*valor"
    ]

    # Hints de entidades
    entity_hints = {
        "count": {"pattern": r"(\d+).*ultim"}
    }

    def run(self, entities, core):
        # Obtener conversaciones para análisis (default últimas 10)
        count = 10
        if "count" in entities and entities["count"]:
            try:
                count = int(entities["count"][0]) if isinstance(entities["count"], list) else int(entities["count"])
                count = max(5, min(count, 50))  # Entre 5 y 50
            except (ValueError, TypeError):
                count = 10

        conversations = core.storage.get_last_conversations(count)

        if not conversations:
            return {
                "summary": "No hay suficientes interacciones para analizar.",
                "classification": "vacía",
                "value_level": "bajo",
                "detected_patterns": [],
                "next_best_actions": ["Comienza una conversación para generar valor."]
            }

        # Análisis básico
        analysis = self._analyze_conversations(conversations)

        # Usar LLM para síntesis si hay suficientes datos
        if len(conversations) >= 5:
            analysis = self._enhance_with_llm(analysis, conversations, core)

        return analysis

    def _analyze_conversations(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Análisis básico de conversaciones"""
        total_interactions = len(conversations)
        sources = [conv["source"] for conv in conversations]
        user_inputs = [conv["user_input"] for conv in conversations]

        # Clasificación
        skill_count = sources.count("skill")
        llm_count = sources.count("llm")
        unknown_count = sources.count("unknown")

        if skill_count > llm_count * 1.5:
            classification = "técnica"
        elif llm_count > skill_count * 1.5:
            classification = "conversacional"
        else:
            classification = "mixta"

        # Nivel de valor
        unique_sources = len(set(sources))
        intent_diversity = len(set(self._extract_intents(user_inputs)))

        if unique_sources >= 3 and intent_diversity >= 4:
            value_level = "alto"
        elif unique_sources >= 2 or intent_diversity >= 2:
            value_level = "medio"
        else:
            value_level = "bajo"

        # Patrones detectados
        patterns = []
        if skill_count > 0:
            patterns.append("uso de comandos específicos")
        if llm_count > 0:
            patterns.append("preguntas abiertas o conversacionales")
        if unknown_count > total_interactions * 0.3:
            patterns.append("intents no reconocidos frecuentemente")
        if total_interactions >= 8:
            patterns.append("sesión prolongada")
        if len(set(user_inputs)) < total_interactions * 0.7:
            patterns.append("repetición de consultas")

        # Acciones siguientes
        actions = []
        if classification == "técnica":
            actions.append("Explora más funcionalidades del sistema")
            actions.append("Prueba comandos avanzados")
        elif classification == "conversacional":
            actions.append("Haz preguntas más específicas para activar skills")
            actions.append("Pide resúmenes o análisis")
        else:
            actions.append("Continua combinando comandos y conversación")
            actions.append("Pide feedback sobre la sesión")

        if value_level == "bajo":
            actions.append("Intenta tareas más diversas")
        elif value_level == "alto":
            actions.append("Documenta lo aprendido para referencia futura")

        # Resumen básico
        summary = f"Sesión de {total_interactions} interacciones, clasificada como {classification} con valor {value_level}."

        return {
            "summary": summary,
            "classification": classification,
            "value_level": value_level,
            "detected_patterns": patterns,
            "next_best_actions": actions
        }

    def _extract_intents(self, user_inputs: List[str]) -> List[str]:
        """Extrae intents aproximados de inputs de usuario"""
        intents = []
        for input_text in user_inputs:
            text = input_text.lower()
            if any(word in text for word in ["hora", "time", "fecha"]):
                intents.append("get_time")
            elif any(word in text for word in ["abrir", "abre", "open", "launch"]):
                intents.append("open_app")
            elif any(word in text for word in ["estado", "status", "cpu", "memoria"]):
                intents.append("system_status")
            elif any(word in text for word in ["nota", "anota", "note"]):
                intents.append("create_note")
            elif any(word in text for word in ["busca", "encuentra", "search", "find"]):
                intents.append("search_file")
            elif any(word in text for word in ["resum", "actividad", "haciendo"]):
                intents.append("summarize")
            else:
                intents.append("unknown")
        return intents

    def _enhance_with_llm(self, analysis: Dict[str, Any], conversations: List[Dict[str, Any]], core) -> Dict[str, Any]:
        """Mejora el análisis con LLM para insights más profundos"""
        # Preparar contexto de la sesión
        context_lines = []
        for conv in conversations[-5:]:  # Últimas 5 para no sobrecargar
            context_lines.append(f"U: {conv['user_input']}")
            context_lines.append(f"J: {conv['response'][:50]}...")

        session_context = "\n".join(context_lines)

        prompt = f"""Analiza esta sesión de usuario y proporciona insights estructurados.

Contexto de la sesión (últimas interacciones):
{session_context}

Análisis básico actual:
- Clasificación: {analysis['classification']}
- Nivel de valor: {analysis['value_level']}
- Patrones: {', '.join(analysis['detected_patterns'])}

Proporciona:
1. Un resumen mejorado de 1-2 oraciones
2. Sugerencias de acciones siguientes más específicas

Responde en formato JSON:
{{
  "enhanced_summary": "...",
  "additional_actions": ["acción 1", "acción 2"]
}}"""

        try:
            llm_response = core.llm_manager.generate(prompt, "")
            # Parsear JSON (simple, asumir formato correcto)
            if "{" in llm_response and "}" in llm_response:
                start = llm_response.find("{")
                end = llm_response.rfind("}") + 1
                json_str = llm_response[start:end]
                import json
                enhancement = json.loads(json_str)
                analysis["summary"] = enhancement.get("enhanced_summary", analysis["summary"])
                analysis["next_best_actions"].extend(enhancement.get("additional_actions", []))
        except Exception:
            # Si falla, mantener análisis básico
            pass

        return analysis