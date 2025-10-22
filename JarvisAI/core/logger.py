import logging
from logging.handlers import RotatingFileHandler
import os
import traceback

LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name="Jarvis", global_log=True):
    """
    name: nombre del módulo (Dispatcher, Memory, SkillClima...)
    global_log: si True, también registra en un log general para todo Jarvis
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Formato
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

        # Console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File por módulo
        fh = RotatingFileHandler(f"{LOG_DIR}/{name}.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Log global
        if global_log and name != "Jarvis_Global":
            gh = RotatingFileHandler(f"{LOG_DIR}/Jarvis_Global.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
            gh.setLevel(logging.DEBUG)
            gh.setFormatter(formatter)
            logger.addHandler(gh)

    return logger

def log_exception(logger, msg="Error detectado"):
    """
    Logea error completo con traceback en consola, módulo y log global
    """
    tb = traceback.format_exc()
    logger.error(f"{msg}\n{tb}")
