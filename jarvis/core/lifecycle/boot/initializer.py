# core/lifecycle/boot/initializer.py
import os
import json

from core.lifecycle.consent import get_or_request_data_collection_consent


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

        if cfg.get("ask_consent", False) and "data_collection" not in cfg:
            cfg["data_collection"] = get_or_request_data_collection_consent(
                app_name=str(cfg.get("name", "Jarvis")),
                app_version=str(cfg.get("version", "unknown"))
            )
        cfg.setdefault("data_collection", False)

        # init logging minimal
        self.core._log("INIT", f"Initializer applied. name={cfg.get('name')} version={cfg.get('version')}")
