# actions/skills/dispatcher.py

class SkillDispatcher:
    def __init__(self):
        self.registry = {}
        self.skills = {}   # <--- ESTO FALTABA
        

    def register(self, intent_name, skill_cls):
        self.registry[intent_name] = skill_cls

    def dispatch(self, intent, entities, system_state):
        if intent not in self.registry:
            return {"error": f"skill_not_implemented:{intent}"}

        skill = self.registry[intent]()
        return skill.run(entities, system_state)
