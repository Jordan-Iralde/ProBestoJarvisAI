import re
from brain.nlu.normalizer import Normalizer


class IntentParser:
    def __init__(self, skills_registry):
        """
        skills_registry debe ser: { intent_name: SkillClass }
        """
        self.norm = Normalizer()
        self.mapping = self._load_patterns(skills_registry)

    # --------------------------------------------
    # Cargar patrones declarados por cada skill
    # --------------------------------------------
    def _load_patterns(self, skills_registry):
        patterns = {}

        for intent, SkillClass in skills_registry.items():
            skill_patterns = getattr(SkillClass, "patterns", None)

            if not skill_patterns or not isinstance(skill_patterns, list):
                continue

            patterns[intent] = skill_patterns

        return patterns

    # --------------------------------------------
    # Inferencia por entidades (prioridad máxima)
    # --------------------------------------------
    def _infer_from_entities(self, entities):
        if not entities:
            return None

        # reglas dominantes
        if entities.get("app"):
            return "open_app"

        if entities.get("file"):
            return "search_file"

        if entities.get("time") or entities.get("date"):
            return "schedule"

        if entities.get("number") and entities.get("duration"):
            return "reminder"

        return None

    # --------------------------------------------
    # Pipeline principal
    # --------------------------------------------
    def parse(self, text: str, entities: dict):
        t = self.norm.run(text)

        # 1. prioridad absoluta: entidades
        inferred = self._infer_from_entities(entities)
        if inferred:
            return inferred

        # 2. patrones dinámicos por skill
        for intent, patterns in self.mapping.items():
            for p in patterns:
                if re.search(p, t):
                    return intent

        # 3. fallback
        return "unknown"
