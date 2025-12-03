# actions/skills/open_app.py
from actions.base.skill import Skill
from actions.system.app_control import open_application

class OpenAppSkill(Skill):
    def run(self, entities, system_state):
        app = entities.get("app")
        if not app:
            return {"error": "missing_app_name"}

        ok = open_application(app)
        return {"status": "ok" if ok else "fail", "app": app}
