from core.logger import get_logger

logger = get_logger("EventBus")

class EventBus:
    def __init__(self, logger=logger):
        self.subscribers = {}
        self.logger = logger

    def subscribe(self, event_name, fn):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(fn)
        self.logger.info(f"Suscrito a evento: {event_name} -> {fn.__name__}")

    def publish(self, event_name, data=None):
        self.logger.info(f"Evento publicado: {event_name} | datos: {data}")
        for fn in self.subscribers.get(event_name, []):
            try:
                fn(data)
            except Exception as e:
                self.logger.error(f"Error en evento {event_name} -> {fn.__name__}: {e}")
'''

2. Event Bus (event_bus.py)

Funciona como pub/sub interno:

Skills, memoria, VIS y GUI se suscriben a eventos.
No dependen unos de otros directamente.
Escalable para acciones en background o cross-skill.
'''