# actions/skills/get_time.py
from datetime import datetime


class GetTimeSkill:
    """Devuelve la hora y fecha actual"""
    
    # Patrones para detección
    patterns = [
        r"\b(hora|time|que hora|qué hora)\b",
        r"\b(fecha|date|dia|día)\b",
        r"\b(reloj)\b"
    ]
    
    # Hints de entidades (opcional, para auto-registro)
    entity_hints = {
        "time_query": {"pattern": r"\b(hora|time)\b"}
    }
    
    def run(self, entities, core):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
        day_name = now.strftime("%A")
        
        return {
            "time": time_str,
            "date": date_str,
            "day": day_name,
            "timestamp": now.timestamp()
        }
