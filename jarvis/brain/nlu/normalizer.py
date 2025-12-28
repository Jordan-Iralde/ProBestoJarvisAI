# brain/nlu/normalizer.py
import unicodedata
import re


class Normalizer:
    """
    Normalizer v2 - Extensible y con memoria de patrones
    """
    def __init__(self, custom_fillers=None):
        # Fillers base (expandible)
        self.filler = [
            "por favor", "podes", "podrias", "quiero que",
            "che", "uh", "hey", "tipo", "me podes",
            "me podrias", "si podes", "si podrias",
            "jarvis", "oye", "escucha"
        ]
        
        # Permitir agregar fillers custom
        if custom_fillers:
            self.filler.extend(custom_fillers)
        
        # Contracciones comunes (español)
        self.contractions = {
            "pa": "para",
            "q": "que",
            "x": "por",
            "xq": "porque",
            "tb": "tambien",
            "tmb": "tambien"
        }
    
    def run(self, text: str) -> str:
        """Normaliza texto conservando contexto importante"""
        t = text.lower()

        # Quitar acentos
        t = ''.join(
            c for c in unicodedata.normalize('NFD', t)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Expandir contracciones
        for short, full in self.contractions.items():
            t = re.sub(r'\b' + short + r'\b', full, t)

        # Remover fillers
        for f in self.filler:
            t = t.replace(f, "")

        # Normalizar espacios
        t = re.sub(r"\s+", " ", t).strip()
        
        return t
    
    def add_filler(self, filler: str):
        """Permite agregar fillers dinámicamente"""
        if filler.lower() not in self.filler:
            self.filler.append(filler.lower())
    
    def add_contraction(self, short: str, full: str):
        """Permite agregar contracciones dinámicamente"""
        self.contractions[short.lower()] = full.lower()