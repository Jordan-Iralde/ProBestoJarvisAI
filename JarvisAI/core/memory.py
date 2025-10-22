from core.logger import get_logger
import sqlite3

logger = get_logger("Memory")

class Memory:
    def __init__(self, db_path="data/memory.db", logger=logger):
        self.conn = sqlite3.connect(db_path)
        self.logger = logger
        self.conn.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")

    def set(self, key, value):
        self.conn.execute("REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()
        self.logger.info(f"Memory set: {key} -> {value}")

    def get(self, key):
        cur = self.conn.execute("SELECT value FROM memory WHERE key=?", (key,))
        res = cur.fetchone()
        self.logger.info(f"Memory get: {key} -> {res[0] if res else None}")
        return res[0] if res else None

    def append(self, key, value):
        existing = self.get(key)
        if existing:
            value = existing + ";" + value
        self.set(key, value)

'''
Capa simple para persistencia temporal o permanente.

API clara: get(key), set(key, value), append(key, value), search(query)
Inicialmente SQLite o JSON, luego podés migrar a Redis / embeddings / vector DB.
'''