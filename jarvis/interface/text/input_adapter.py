class CLIInput:
    def __init__(self, eventbus):
        self.bus = eventbus

    def poll(self):
        if not self._ready():
            return

        txt = input(">> ").strip()
        if txt:
            self.bus.emit("input.text", {"text": txt})
            # lanzar nlu
            from brain.nlu.pipeline import NLUPipeline
            nlu = NLUPipeline()
            nlu.process(txt, self.bus)

    def _ready(self):
        # CLI siempre está listo
        return True
