import importlib
import json
import os
import sys

class Dispatcher:
    def __init__(self, skills_path="skills"):
        self.skills = []
        self.skills_path = os.path.abspath(skills_path)

        # Agregar skills al PYTHONPATH para importlib
        sys.path.append(os.path.dirname(self.skills_path))

        # Crear carpeta si no existe
        os.makedirs(self.skills_path, exist_ok=True)
        print(f"[Dispatcher] Carpeta de skills lista en: {self.skills_path}")

        self.load_skills()

    def load_skills(self):
        for skill_folder in os.listdir(self.skills_path):
            folder_path = os.path.join(self.skills_path, skill_folder)

            if not os.path.isdir(folder_path):
                continue

            try:
                skill_json = os.path.join(folder_path, "skill.json")
                if not os.path.isfile(skill_json):
                    print(f"[Dispatcher] skill.json faltante en {folder_path}, se omite.")
                    continue

                with open(skill_json, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                module = importlib.import_module(f"skills.{skill_folder}.skill")
                run_fn = getattr(module, "run", None)

                if not callable(run_fn):
                    print(f"[Dispatcher] {skill_folder} no tiene run(), se omite.")
                    continue

                self.skills.append({"meta": meta, "run": run_fn})
                print(f"[Dispatcher] Skill cargado: {meta['name']}")

            except Exception as e:
                print(f"[Dispatcher] Error cargando skill {skill_folder}: {e}")

    def dispatch(self, text: str):
        text_lower = text.lower()
        for s in self.skills:
            if any(k.lower() in text_lower for k in s["meta"]["keywords"]):
                print(f"[Dispatcher] Ejecutando skill: {s['meta']['name']}")
                return s["run"](text)
        return "No entendí el comando."


# =========================
# TEST DE PRUEBA AUTOMÁTICO
# =========================
if __name__ == "__main__":
    # Crear skill de prueba si no existe
    os.makedirs("JarvisAi/skills/testskill", exist_ok=True)

    with open("skills/__init__.py", "w") as f:
        f.write("")  # marcar como paquete
    with open("skills/testskill/__init__.py", "w") as f:
        f.write("")

    with open("skills/testskill/skill.json", "w", encoding="utf-8") as f:
        json.dump({
            "name": "Test Skill",
            "keywords": ["hola", "test"]
        }, f, indent=4)

    with open("skills/testskill/skill.py", "w", encoding="utf-8") as f:
        f.write("def run(text):\n    return 'Skill ejecutado OK'")

    # Ejecutar dispatcher
    d = Dispatcher()
    print("\n[Test] Resultado:", d.dispatch("hola jarvis, estás ahí?"))
