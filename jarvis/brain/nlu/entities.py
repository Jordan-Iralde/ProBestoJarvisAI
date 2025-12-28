# brain/nlu/entities.py
import re
import unicodedata


def normalize(text):
    """Helper de normalización rápida"""
    t = text.lower()
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')
    return t


class EntityExtractor:
    """
    EntityExtractor v2 - Auto-registro y learning-ready
    
    Features:
    - Auto-descubre entidades de skills registradas
    - Aprende nuevos patrones dinámicamente
    - Sistema de confianza para entidades
    """
    
    def __init__(self, skills_registry=None):
        # Listas base (se expanden automáticamente)
        self.app_list = [
            "whatsapp", "wa", "chrome", "spotify",
            "discord", "vscode", "telegram", "youtube", 
            "notion", "notepad", "calculator", "calc",
            "explorer", "cmd", "firefox", "edge"
        ]
        
        # Patrones regex base
        self.regex = {
            "time": r"\b(\d{1,2}(:\d{2})?\s*(am|pm)?)\b",
            "date": r"\b(\d{1,2}/\d{1,2}(/\d{2,4})?|hoy|mañana|ma[ñn]ana|pasado mañana)\b",
            "duration": r"\b(en|dentro de)\s+(\d{1,3})\s*(minutos?|min|horas?|hs|h)\b",
            "number": r"\b\d+\b",
            "file": r"\b([a-z0-9_\-]+\.(txt|pdf|docx?|xlsx?|py|js|json|md))\b",
            "path": r"\b([a-z]:[\\\/][^\s]+|\/[^\s]+)\b"
        }
        
        # Patrones contextuales (aprenden de uso)
        self.contextual_patterns = {
            "app": [
                r"abr[ie]\s+([a-z0-9]+)",
                r"ejecuta\s+([a-z0-9]+)",
                r"inicia\s+([a-z0-9]+)",
                r"abre?\s+([a-z0-9]+)",
                r"lanza\s+([a-z0-9]+)"
            ],
            "note_content": [
                r"nota\s+(.+)",
                r"anota\s+(.+)",
                r"escrib[ie]\s+(.+)"
            ],
            "search_query": [
                r"busca\s+(.+)",
                r"encuentra\s+(.+)",
                r"donde esta\s+(.+)"
            ]
        }
        
        # Auto-registro de entidades desde skills
        if skills_registry:
            self._register_from_skills(skills_registry)
        
        # Sistema de confianza (para learning)
        self.confidence_scores = {}
    
    def _register_from_skills(self, skills_registry):
        """
        Auto-descubre entidades de las skills registradas.
        Las skills pueden definir 'entity_hints' para auto-registro.
        """
        for intent, SkillClass in skills_registry.items():
            # Si la skill define entidades esperadas
            entity_hints = getattr(SkillClass, "entity_hints", None)
            if entity_hints:
                for entity_type, values in entity_hints.items():
                    if entity_type == "app" and isinstance(values, list):
                        self.app_list.extend(values)
                    elif isinstance(values, dict) and "pattern" in values:
                        self.contextual_patterns.setdefault(entity_type, [])
                        self.contextual_patterns[entity_type].append(values["pattern"])
        
        # Eliminar duplicados en app_list
        self.app_list = list(set(self.app_list))
    
    def extract(self, raw_text: str) -> dict:
        """
        Extrae entidades con sistema de confianza.
        
        Returns:
            dict: {entity_type: [values], "confidence": {entity_type: score}}
        """
        text = normalize(raw_text)
        out = {}
        confidence = {}
        
        # 1. Apps (alta prioridad)
        detected_apps = [a for a in self.app_list if a in text]
        
        # Si no detectó apps, buscar con patrones contextuales
        if not detected_apps and "app" in self.contextual_patterns:
            for pattern in self.contextual_patterns["app"]:
                m = re.search(pattern, text)
                if m:
                    detected_apps = [m.group(1)]
                    confidence["app"] = 0.8  # Confianza media
                    break
        else:
            confidence["app"] = 1.0 if detected_apps else 0.0
        
        out["app"] = detected_apps
        
        # 2. Patrones regex generales
        for name, pattern in self.regex.items():
            matches = re.findall(pattern, text)
            results = []
            for m in matches:
                value = m[0] if isinstance(m, tuple) else m
                results.append(value)
            out[name] = results
            confidence[name] = 1.0 if results else 0.0
        
        # 3. Patrones contextuales adicionales
        for entity_type, patterns in self.contextual_patterns.items():
            if entity_type == "app":
                continue  # Ya procesado
            
            for pattern in patterns:
                m = re.search(pattern, text)
                if m:
                    out[entity_type] = m.group(1) if m.groups() else m.group(0)
                    confidence[entity_type] = 0.9
                    break
        
        # Agregar scores de confianza
        out["_confidence"] = confidence
        
        return out
    
    def learn_entity(self, entity_type: str, value: str, context: str = None):
        """
        Aprende una nueva entidad desde contexto de uso.
        
        Args:
            entity_type: Tipo de entidad (app, file, etc.)
            value: Valor de la entidad
            context: Texto original donde apareció (opcional)
        """
        if entity_type == "app" and value not in self.app_list:
            self.app_list.append(value)
            print(f"[ENTITIES] Learned new app: {value}")
        
        # Incrementar confianza
        key = f"{entity_type}:{value}"
        self.confidence_scores[key] = self.confidence_scores.get(key, 0.5) + 0.1
        
        # Si hay contexto, extraer patrón
        if context and value in context:
            pattern = self._extract_pattern(context, value)
            if pattern:
                self.contextual_patterns.setdefault(entity_type, [])
                if pattern not in self.contextual_patterns[entity_type]:
                    self.contextual_patterns[entity_type].append(pattern)
                    print(f"[ENTITIES] Learned new pattern for {entity_type}: {pattern}")
    
    def _extract_pattern(self, context: str, value: str):
        """Intenta extraer un patrón regex desde el contexto"""
        # Buscar verbos comunes antes del valor
        words_before = context[:context.find(value)].strip().split()
        if words_before:
            verb = words_before[-1]
            return rf"\b{verb}\s+([a-z0-9]+)"
        return None
    
    def add_regex_pattern(self, entity_type: str, pattern: str):
        """Permite agregar patrones regex manualmente"""
        self.regex[entity_type] = pattern
        print(f"[ENTITIES] Added regex pattern for {entity_type}")
    
    def get_stats(self):
        """Retorna estadísticas de entidades conocidas"""
        return {
            "apps": len(self.app_list),
            "regex_patterns": len(self.regex),
            "contextual_patterns": sum(len(v) for v in self.contextual_patterns.values()),
            "learned_entities": len(self.confidence_scores)
        }