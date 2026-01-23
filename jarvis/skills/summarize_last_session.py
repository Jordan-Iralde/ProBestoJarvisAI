# skills/summarize_last_session.py
import re
import time


class SummarizeLastSessionSkill:
    """Genera un resumen de la sesión actual desde el último boot"""

    # Patrones para detección
    patterns = [
        r"resumir.*sesión",
        r"sesión.*actual",
        r"última.*sesión",
        r"resumen.*sesión",
        r"qué.*pasó.*sesión"
    ]

    # Hints de entidades
    entity_hints = {}

    def run(self, entities, core):
        # Obtener conversaciones desde el inicio de la sesión
        conversations = core.storage.get_conversations_since(core.start_time)

        if not conversations:
            return {
                "summary": "Esta sesión aún no tiene interacciones registradas.",
                "interactions_count": 0,
                "sources": [],
                "session_duration_minutes": round((time.time() - core.start_time) / 60, 1)
            }

        interactions_count = len(conversations)
        sources = list(set(conv["source"] for conv in conversations))
        session_duration = round((time.time() - core.start_time) / 60, 1)

        # Generar resumen
        if interactions_count <= 3:
            # Reglas simples
            summary_parts = []
            for i, conv in enumerate(conversations, 1):
                user_input = conv["user_input"][:40] + "..." if len(conv["user_input"]) > 40 else conv["user_input"]
                summary_parts.append(f"{i}. {user_input}")
            summary = f"En esta sesión: {'; '.join(summary_parts)}."
        else:
            # Usar LLM para resumen
            context_lines = []
            for conv in conversations:
                context_lines.append(f"Usuario: {conv['user_input']}")
                context_lines.append(f"Jarvis: {conv['response'][:80]}...")
            context_text = "\n".join(context_lines)

            prompt = f"""Resume la sesión actual del usuario en 1-2 oraciones concisas.
Sesión de {session_duration} minutos con {interactions_count} interacciones:
{context_text}

Resumen de sesión:"""

            summary = core.llm_manager.generate(prompt, "").strip()
            if not summary:
                summary = f"Sesión de {session_duration} minutos con {interactions_count} interacciones."

        return {
            "summary": summary,
            "interactions_count": interactions_count,
            "sources": sources,
            "session_duration_minutes": session_duration
        }