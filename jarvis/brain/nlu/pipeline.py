# brain/nlu/pipeline.py
import traceback
from brain.nlu.normalizer import Normalizer
from brain.nlu.entities import EntityExtractor
from brain.nlu.parser import IntentParser


class NLUPipeline:
    def __init__(self, skills_registry, debug=False):
        self.norm = Normalizer()
        self.entities = EntityExtractor()
        self.intent = IntentParser(skills_registry)
        self.debug = debug
        self.skills_registry = skills_registry

    def _log(self, *msg):
        if self.debug:
            print("[NLU]", *msg)

    def process(self, text: str, eventbus):
        try:
            raw = text.strip()
            if not raw:
                return

            # 1. Normalizar
            clean = self.norm.run(raw)
            self._log("normalized:", clean)

            # 2. Extraer entidades
            ent = self.entities.extract(clean)
            self._log("entities:", ent)

            eventbus.emit("nlu.entities.detected", {
                "raw": raw,
                "normalized": clean,
                "entities": ent
            })

            # 3. Intent basado en entidades + patrones
            intent_name = self.intent.parse(clean, ent)
            self._log("intent:", intent_name)

            eventbus.emit("nlu.intent", {
                "intent": intent_name,
                "entities": ent,
                "raw": raw,
                "normalized": clean
            })

        except Exception as e:
            print("[NLU_ERROR]", e)
            traceback.print_exc()
            eventbus.emit("nlu.error", {
                "error": str(e),
                "text": text
            })
