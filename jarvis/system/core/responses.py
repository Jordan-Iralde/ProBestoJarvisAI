# system/core/responses.py
from typing import Any


class ResponseFormatter:
    """Formateador de respuestas de las skills, separado para escalabilidad"""
    def format(self, intent: str, dispatch_result: dict) -> str:
        if not intent:
            return "No recibí ninguna intención."

        if intent == "unknown":
            # TODO: obtener lista de skills desde dispatcher
            available = "open_app, get_time, system_status, create_note, search_file"
            return "No entendí el comando. Probá con: " + available

        if not dispatch_result.get("success", True):
            err = dispatch_result.get("error") or "error"
            return f"No pude ejecutar '{intent}': {err}"

        payload = dispatch_result.get("result")
        if isinstance(payload, dict) and payload.get("success") is False:
            err = payload.get("error") or "error"
            return f"No pude ejecutar '{intent}': {err}"

        if intent == "open_app" and isinstance(payload, dict):
            return f"Abriendo {payload.get('app', 'la aplicación')}."
        if intent == "get_time" and isinstance(payload, dict):
            return f"Son las {payload.get('time')} del {payload.get('date')}."
        if intent == "system_status" and isinstance(payload, dict):
            cpu = (payload.get("cpu") or {}).get("percent")
            mem = (payload.get("memory") or {}).get("percent")
            if cpu is not None and mem is not None:
                return f"Estado del sistema: CPU {cpu}% | RAM {mem}%."
            return "Estado del sistema obtenido."
        if intent == "create_note" and isinstance(payload, dict):
            return f"Nota creada: {payload.get('filename', 'ok')}."
        if intent == "search_file" and isinstance(payload, dict):
            return f"Búsqueda completada. Encontré {payload.get('count', 0)} resultados."

        return f"Listo: {intent}."
