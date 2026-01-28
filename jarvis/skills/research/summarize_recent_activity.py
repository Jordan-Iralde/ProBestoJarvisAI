# skills/summarize_recent_activity.py
import re


class SummarizeRecentActivitySkill:
    """Genera un resumen de la actividad reciente del usuario"""

    # Patrones para detección
    patterns = [
        r"resumir.*actividad",
        r"resumen.*reciente",
        r"que.*hice.*reciente",
        r"actividad.*reciente",
        r"ultimas.*interacciones"
    ]

    # Hints de entidades
    entity_hints = {
        "count": {"pattern": r"\b(\d+)\b.*\b(últimas|ultima|reciente|recent)\b"}
    }

    def run(self, entities, core):
        # Extraer número de interacciones (default 5)
        count = 5
        if "count" in entities and entities["count"]:
            try:
                count = int(entities["count"][0]) if isinstance(entities["count"], list) else int(entities["count"])
                count = max(1, min(count, 20))  # Limitar entre 1 y 20
            except (ValueError, TypeError):
                count = 5

        # Obtener últimas conversaciones desde Storage
        conversations = core.storage.get_last_conversations(count)

        if not conversations:
            return {
                "summary": "No hay actividad reciente registrada.",
                "interactions_count": 0,
                "sources": []
            }

        interactions_count = len(conversations)
        sources = list(set(conv["source"] for conv in conversations))

        # Generar resumen
        if interactions_count <= 3:
            # Reglas simples: concatenación estructurada
            summary_parts = []
            for i, conv in enumerate(conversations, 1):
                user_input = conv["user_input"][:50] + "..." if len(conv["user_input"]) > 50 else conv["user_input"]
                summary_parts.append(f"{i}. {user_input}")
            summary = f"En las últimas interacciones: {'; '.join(summary_parts)}."
        else:
            # Usar LLM para resumen inteligente
            # Preparar contexto reducido (solo user inputs)
            context_lines = []
            for conv in conversations:
                context_lines.append(f"Usuario: {conv['user_input']}")
                context_lines.append(f"Jarvis: {conv['response'][:100]}...")
            context_text = "\n".join(context_lines)

            prompt = f"""Resume la actividad reciente del usuario en una oración clara y accionable.
Contexto de las últimas {interactions_count} interacciones:
{context_text}

Resumen:"""

            summary = core.llm_manager.generate(prompt, "").strip()
            if not summary:
                summary = "No se pudo generar un resumen inteligente."

        return {
            "summary": summary,
            "interactions_count": interactions_count,
            "sources": sources
        }