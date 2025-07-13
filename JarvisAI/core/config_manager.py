# core/config_manager.py

import os, json
from cryptography.fernet import Fernet
from config.settings import config

LOCAL_CFG = os.path.expanduser("~/.jarvis/config.enc")

class ConfigManager:
    def __init__(self):
        self.path = LOCAL_CFG
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        # Generar o leer clave
        keyfile = os.path.expanduser("~/.jarvis/key.key")
        if not os.path.isfile(keyfile):
            key = Fernet.generate_key()
            with open(keyfile, "wb") as f: f.write(key)
        else:
            key = open(keyfile, "rb").read()
        self.cipher = Fernet(key)

    def load_or_init(self):
        if os.path.isfile(self.path):
            data = self.cipher.decrypt(open(self.path, "rb").read())
            return json.loads(data)
        # Si no existe, crear default
        default = {"preferred_mode": None, "usage_count": 0}
        self.save(default)
        return default

    def save(self, data: dict):
        enc = self.cipher.encrypt(json.dumps(data).encode())
        with open(self.path, "wb") as f:
            f.write(enc)
