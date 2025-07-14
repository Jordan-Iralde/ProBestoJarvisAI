# config/settings.py

import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

# Carga .env
load_dotenv()

# Directorio base del proyecto (donde está este archivo)
BASE_DIR = Path(__file__).resolve().parent.parent

def load_config(path=None):
    # Si no dan path, buscar environment.yaml en config/
    cfg_file = Path(path) if path else BASE_DIR / "config" / "environments.yaml"
    if not cfg_file.is_file():
        raise FileNotFoundError(
            f"No se encontró archivo de configuración: {cfg_file}"
        )
    with open(cfg_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class Settings:
    def __init__(self):
        self.env = os.getenv("ENV", "dev")
        self.config = load_config()                   # ahora apunta bien
        self.settings = self.config.get(self.env, {})
        self.debug = self.settings.get("debug", False)

        # Claves
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.DB_URI          = os.getenv("MONGO_URI")

        # Directorio de logs
        self.LOG_DIR = self.settings.get("log_dir", "logs/")
        os.makedirs(self.LOG_DIR, exist_ok=True)

        # Flags varios
        self.voice_enabled = self.settings.get("voice_enabled", True)
        dc = self.settings.get("data_collection", {})
        
        self.dc_enabled        = dc.get("enabled", False)
        self.dc_interval       = dc.get("interval_sec", 60)
        self.dc_metrics        = dc.get("metrics", [])

        fl = self.settings.get("forced_load", {})
        self.fl_enabled        = fl.get("enabled", False)
        self.fl_cpu_percent    = fl.get("cpu_load_percent", 0)
        self.fl_mem_mb         = fl.get("mem_load_mb", 0)

# Singleton
config = Settings()
