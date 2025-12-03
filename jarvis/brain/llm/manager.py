class LLMManager:
    def __init__(self):
        self.enabled = False

    def generate(self, prompt: str) -> str:
        return "[LLM offline placeholder: no model loaded]"
