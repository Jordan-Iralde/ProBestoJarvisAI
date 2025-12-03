import unicodedata
import re

class Normalizer:
    def __init__(self):
        self.filler = [
            "por favor", "podes", "podrias", "quiero que",
            "che", "uh", "hey", "tipo", "me podes",
            "me podrias", "si podes", "si podrias"
        ]

    def run(self, text: str) -> str:
        t = text.lower()

        # quitar acentos
        t = ''.join(
            c for c in unicodedata.normalize('NFD', t)
            if unicodedata.category(c) != 'Mn'
        )

        for f in self.filler:
            t = t.replace(f, "")

        t = re.sub(r"\s+", " ", t).strip()
        return t
