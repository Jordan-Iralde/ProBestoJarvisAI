# main.py
from core.logger import get_logger
from core.dispatcher import Dispatcher
from core.event_bus import EventBus
from core.memory import Memory
from modules.voz_jarvis import virtual_voice  # import the instance, not the class

logger = get_logger("Main")
logger.info("=== Iniciando Jarvis ===")

dispatcher = Dispatcher(logger=get_logger("Dispatcher"))
event_bus = EventBus(logger=get_logger("EventBus"))
memory = Memory(logger=get_logger("Memory"))

def procesar_comando(texto):
    respuesta = dispatcher.dispatch(texto)
    if respuesta:
        logger.info(f"Respuesta a comando: {respuesta}")
        # use the running singleton instance
        virtual_voice.hablar(respuesta)

def main_loop():
    try:
        while True:
            comando = input("Decime algo > ")
            if comando.lower() in ["salir", "exit"]:
                logger.info("Cerrando Jarvis.")
                break
            procesar_comando(comando)
    except KeyboardInterrupt:
        logger.info("Interrupted by user (Ctrl+C).")
    finally:
        # ensure clean shutdown so the thread can finish last utterance
        try:
            virtual_voice.shutdown()
        except Exception:
            logger.exception("Error shutting down virtual_voice")

if __name__ == "__main__":
    main_loop()
