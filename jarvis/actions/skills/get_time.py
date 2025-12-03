# actions/skills/get_time.py
from actions.base.skill import Skill
import datetime

class GetTimeSkill(Skill):
    def run(self, entities, system_state):
        now = datetime.datetime.now().strftime("%H:%M")
        return {"time": now}
