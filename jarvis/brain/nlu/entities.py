import re
import unicodedata

def normalize(text):
    t = text.lower()
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')
    return t

class EntityExtractor:
    def __init__(self):
        self.app_list = [
            "whatsapp","wa","chrome","spotify",
            "discord","vscode","telegram","youtube","notion"
        ]

        self.regex = {
            "time": r"\b(\d{1,2}(:\d{2})?\s*(am|pm)?)\b",
            "date": r"\b(\d{1,2}/\d{1,2}(/\d{2,4})?|hoy|mañana|pasado mañana)\b",
            "duration": r"\b(en|dentro de)\s+(\d{1,3})\s*(minutos|min|horas|hs|h)\b",
            "number": r"\b\d+\b"
        }

    def extract(self, raw_text: str) -> dict:
        text = normalize(raw_text)
        out = {}

        # apps primero
        out["app"] = [a for a in self.app_list if a in text]

        # si no detectó ninguna app y hay “abre X”
        if not out["app"]:
            m = re.search(r"abre\s+([a-z0-9]+)", text)
            if m:
                out["app"] = [m.group(1)]

        # regex generales
        for name, pattern in self.regex.items():
            matches = re.findall(pattern, text)
            results = []
            for m in matches:
                results.append(m[0] if isinstance(m, tuple) else m)
            out[name] = results

        return out
