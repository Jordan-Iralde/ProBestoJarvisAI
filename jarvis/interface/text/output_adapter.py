# interface/text/output_adapter.py
class TextOutput:
    def send(self, text: str):
        if text is None:
            return
        print(text)
