import json
import os
import signal
import sys
from system.core import JarvisCore

def load_config():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "config.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    config = load_config()
    core = JarvisCore(config)

    # boot del sistema
    core.boot()

    # handler de interrupción limpia
    def shutdown(sig, frame):
        print("[SYSTEM] Shutdown solicitado.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # loop principal
    core.run()

if __name__ == "__main__":
    main()
