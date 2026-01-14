# interface/text/input_adapter.py
class CLIInput:
    def __init__(self, eventbus, nlu_pipeline=None, logger=None):
        self.bus = eventbus
        self.nlu = nlu_pipeline  # Recibir el pipeline ya inicializado
        self.logger = logger
        self._running = True

    def poll(self):
        if not self._ready():
            return

        try:
            txt = input(">> ").strip()
            if txt:
                # Emitir evento de input
                self.bus.emit("input.text", {"text": txt})

                # Procesar con NLU si está disponible
                if self.nlu:
                    self.nlu.process(txt, self.bus)
                else:
                    if self.logger:
                        self.logger.warning("NLU pipeline no disponible")
                    else:
                        print("[WARN] NLU pipeline no disponible")
        except EOFError:
            self._running = False
        except KeyboardInterrupt:
            self._running = False

    def _ready(self):
        return self._running

    def stop(self):
        self._running = False
