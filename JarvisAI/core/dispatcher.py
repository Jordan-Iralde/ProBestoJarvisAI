import importlib
import json
import os
from core.logger import get_logger, log_exception

class Dispatcher:
    def __init__(self, skills_path="JarvisAi/skills", logger=None):
        self.logger = logger or get_logger("Dispatcher")
        self.skills = []

        # Absolute and guaranteed folder
        self.skills_path = os.path.abspath(skills_path)
        os.makedirs(self.skills_path, exist_ok=True)
        self.logger.info(f"Skills folder ready at: {self.skills_path}")

        self.load_skills(self.skills_path)

    def load_skills(self, path):
        for skill_folder in os.listdir(path):
            folder_path = os.path.join(path, skill_folder)

            if not os.path.isdir(folder_path):
                continue

            try:
                skill_json_path = os.path.join(folder_path, "skill.json")
                if not os.path.isfile(skill_json_path):
                    self.logger.warning(f"Missing skill.json in {folder_path}, skipping.")
                    continue

                with open(skill_json_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                # dynamic import: skills.<folder>.skill
                module = importlib.import_module(f"skills.{skill_folder}.skill")
                run_fn = getattr(module, "run", None)

                if not callable(run_fn):
                    self.logger.error(f"{skill_folder} has no run() method, skipping.")
                    continue

                self.skills.append({"meta": meta, "run": run_fn})
                self.logger.info(f"Loaded skill: {meta['name']}")

            except Exception:
                log_exception(self.logger, f"Error loading skill {skill_folder}")

    def dispatch(self, texto: str):
        texto_lower = texto.lower()

        for s in self.skills:
            if any(k.lower() in texto_lower for k in s["meta"]["keywords"]):
                self.logger.info(f"Executing skill: {s['meta']['name']}")
                try:
                    return s["run"](texto)
                except Exception:
                    log_exception(self.logger, f"Error executing skill {s['meta']['name']}")
                    return "Skill execution error."

        self.logger.warning(f"No skill found for: {texto}")
        return "I didn’t understand that command."
