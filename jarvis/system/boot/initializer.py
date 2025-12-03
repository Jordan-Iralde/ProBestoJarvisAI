# system/boot/initializer.py
import os
import json

class Initializer:
    REQUIRED_KEYS = ["name", "version"]

    def __init__(self, core):
        self.core = core

    def run(self):
        # config validation
        cfg = self.core.config
        missing = [k for k in self.REQUIRED_KEYS if k not in cfg]
        if missing:
            raise RuntimeError(f"Missing config keys: {missing}")

        # env overrides (simple)
        for k, v in os.environ.items():
            if k.startswith("JARVIS_"):
                key = k[len("JARVIS_"):].lower()
                cfg[key] = v

        # set defaults
        cfg.setdefault("workers", 4)
        cfg.setdefault("log_level", "INFO")

        # init logging minimal
        self.core._log("INIT", f"Initializer applied. name={cfg.get('name')} version={cfg.get('version')}")
