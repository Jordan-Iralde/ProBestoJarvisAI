# actions/skills/system_status.py
from actions.base.skill import Skill
import psutil

class SystemStatusSkill(Skill):
    def run(self, entities, system_state):
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else None
        }
