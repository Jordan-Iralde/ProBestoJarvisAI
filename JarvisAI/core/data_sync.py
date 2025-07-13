# core/data_sync.py

import threading
import time
from pymongo import MongoClient
from core.config_manager import ConfigManager
from config.settings import config

class DataSync:
    def __init__(self):
        uri = config.DB_URI
        self.client = MongoClient(uri)
        self.db = self.client.jarvis_metrics
        self.local_cfg = ConfigManager().load_or_init()

    def collect_payload(self):
        return {
            "installation_id": self.local_cfg.get("installation_id"),
            "timestamp": time.time(),
            "env": config.env,
            "usage": self.local_cfg.get("usage_count"),
            "errors": [],  # Podríamos leer del log
        }

    def send(self):
        payload = self.collect_payload()
        self.db.general.insert_one(payload)

    def start_periodic_sync(self, interval_sec=3600):
        def loop():
            while True:
                try:
                    self.send()
                except Exception:
                    pass
                time.sleep(interval_sec)
        t = threading.Thread(target=loop, daemon=True)
        t.start()
