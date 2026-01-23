import json
import os
import signal
import sys
import argparse
from system.core import JarvisCore

def load_config():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "config.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_daemon_logging():
    """Configura logging para modo daemon"""
    import logging
    from datetime import datetime
    
    log_dir = os.path.join(os.path.expanduser("~"), "Desktop", "JarvisData", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"jarvis_daemon_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Redirigir stdout y stderr a log
    class LogWriter:
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level
        def write(self, message):
            if message.strip():
                self.logger.log(self.level, message.strip())
        def flush(self):
            pass
    
    sys.stdout = LogWriter(logging.getLogger(), logging.INFO)
    sys.stderr = LogWriter(logging.getLogger(), logging.ERROR)

def main():
    parser = argparse.ArgumentParser(description='Jarvis AI Assistant')
    parser.add_argument('--daemon', action='store_true', 
                       help='Run in daemon mode (background, no console)')
    args = parser.parse_args()
    
    if args.daemon:
        setup_daemon_logging()
        print("Jarvis starting in daemon mode...")
    
    config = load_config()
    core = JarvisCore(config)

    # boot del sistema
    core.boot()

    # handler de interrupción limpia
    def shutdown(sig, frame):
        print("[SYSTEM] Shutdown solicitado.")
        core.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # loop principal
    core.run()

if __name__ == "__main__":
    main()
