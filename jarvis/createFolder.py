import os

structure = {
    "jarvis": {
        "system": {
            "boot": ["loader.py", "initializer.py", "diagnostics.py"],
            "runtime": ["events.py", "state.py", "scheduler.py", "watchdog.py"],
            "core.py": None
        },
        "brain": {
            "nlu": ["pipeline.py", "intents.py", "entities.py", "memory.py"],
            "llm": ["manager.py", "models"],
            "reasoning": ["planner.py", "agent.py", "context.py"]
        },
        "actions": {
            "base": ["action.py"],
            "system": ["os_hooks.py", "file_ops.py", "app_control.py"],
            "skills": ["weather.py", "notes.py", "reminders.py", "web_search.py"],
            "automation": ["triggers.py", "rules_engine.py"]
        },
        "io": {
            "audio": ["loop.py", "vad.py", "wakeword.py", "stt.py"],
            "speech": ["tts.py"],
            "text": ["input_adapter.py", "output_adapter.py"],
            "gui": {
                "dashboard": ["api.py", "views.py"],
                "cli": ["cli.py"]
            }
        },
        "modules": {
            "loader.py": None,
            "installed": {
                "example_module": ["module.py"]
            }
        },
        "storage": ["sqlite", "cache", "logs"],
        "tests": ["test_nlu.py", "test_skills.py", "test_runtime.py"],
        "webapp": None,
        "main.py": None,
        "config.json": None
    }
}

def create(path, tree):
    for name, content in tree.items():
        new_path = os.path.join(path, name)
        
        if isinstance(content, dict):
            os.makedirs(new_path, exist_ok=True)
            create(new_path, content)
        elif isinstance(content, list):
            os.makedirs(new_path, exist_ok=True)
            for item in content:
                item_path = os.path.join(new_path, item)
                if "." in item:
                    open(item_path, "w").close()
                else:
                    os.makedirs(item_path, exist_ok=True)
        elif content is None:
            # It's a file
            if "." in name:
                open(new_path, "w").close()
            else:
                os.makedirs(new_path, exist_ok=True)

if __name__ == "__main__":
    base = "."
    create(base, structure)
