# memoria semántica mínima: solo guarda pares texto-intención previos

class SemanticMemory:
    def __init__(self):
        self.store = []

    def add(self, text: str, parsed: dict):
        self.store.append((text, parsed))

    def retrieve(self, text: str):
        text = text.lower()
        hits = []
        for past_text, parsed in self.store:
            if any(w in text for w in past_text.lower().split()):
                hits.append(parsed)
        return hits
