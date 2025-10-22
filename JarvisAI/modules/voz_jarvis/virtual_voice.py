import threading
from queue import Queue, Empty
import pyttsx3
import time
from core.logger import get_logger, log_exception

logger = get_logger("VozJarvis")


class VozJarvis:
    def __init__(self, velocidad=150, idioma='spanish'):
        self.velocidad = velocidad
        self.idioma = idioma
        self._cola = Queue()
        self._stop_event = threading.Event()
        self._interrupt_event = threading.Event()
        self._thread = None
        self._thread_lock = threading.Lock()
        self._engine_ready = threading.Event()

    def _ensure_started(self):
        with self._thread_lock:
            if self._thread is None or not self._thread.is_alive():
                logger.info("[TTS] Iniciando worker thread...")
                self._stop_event.clear()
                self._thread = threading.Thread(target=self._worker, name="TTSWorker", daemon=False)
                self._thread.start()
                started = self._engine_ready.wait(timeout=3)
                if started:
                    logger.info("[TTS] Worker y engine listos")
                else:
                    logger.warning("[TTS] Timeout esperando que engine se inicialice")

    def hablar(self, texto: str):
        self._ensure_started()
        logger.info(f"[TTS] Enqueue: {texto}")
        self._cola.put(texto)

    def hablar_interrupt(self, texto: str):
        self._ensure_started()
        logger.info(f"[TTS] Interrupt and enqueue: {texto}")
        self._interrupt_event.set()
        # Vaciar la cola sin bloquear
        try:
            while True:
                removed = self._cola.get_nowait()
                logger.debug(f"[TTS] Removido de la cola durante interrupt: {removed}")
        except Exception:
            pass
        self._cola.put(texto)

    def shutdown(self, timeout: float = 5.0):
        logger.info("[TTS] Shutdown solicitado")
        self._stop_event.set()
        self._cola.put(None)
        if self._thread:
            logger.info("[TTS] Esperando que el worker termine...")
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("[TTS] Worker no respondió al shutdown dentro del timeout")
        logger.info("[TTS] Shutdown completo")

    def _worker(self):
        logger.info("[TTS] Worker thread iniciado")
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.velocidad)
            self._select_voice(engine)
            self._engine_ready.set()
            logger.info(f"[TTS] Engine inicializado con voz: {engine.getProperty('voice')}")
        except Exception:
            log_exception(logger, "[TTS] Error inicializando engine")
            self._engine_ready.set()
            return

        while not self._stop_event.is_set():
            try:
                item = self._cola.get(timeout=0.2)
            except Empty:
                continue

            if item is None:
                break

            logger.info(f"[TTS] Procesando: {item}")
            try:
                if self._interrupt_event.is_set():
                    try:
                        engine.stop()
                        logger.info("[TTS] Reproducción interrumpida")
                    except Exception:
                        logger.debug("[TTS] engine.stop() falló durante interrupción")
                    self._interrupt_event.clear()

                engine.say(item)
                engine.runAndWait()
                logger.info(f"[TTS] Reproducción completada: {item}")
                time.sleep(0.05)
            except Exception:
                log_exception(logger, "[TTS] Error runAndWait(), reiniciando engine")
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.velocidad)
                    self._select_voice(engine)
                    logger.info("[TTS] Engine reiniciado")
                except Exception:
                    log_exception(logger, "[TTS] Reinicio de engine fallido")
                    break

        try:
            if engine:
                engine.stop()
                logger.info("[TTS] Engine detenido al cerrar worker")
        except Exception:
            pass

    def _select_voice(self, engine):
        try:
            for voice in engine.getProperty('voices'):
                name = (getattr(voice, "name", "") or "").lower()
                langs = getattr(voice, "languages", []) or []
                if self.idioma.lower() in name or any(self.idioma.lower() in str(l).lower() for l in langs):
                    engine.setProperty('voice', voice.id)
                    logger.info(f"[TTS] Voz seleccionada: {voice.name}")
                    break
        except Exception:
            logger.debug("[TTS] No se pudo seleccionar voz por idioma, usando por defecto")


# Instancia global (lazy start)
virtual_voice = VozJarvis()
