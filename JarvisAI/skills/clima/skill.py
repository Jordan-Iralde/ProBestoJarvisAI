from core.logger import get_logger, log_exception
logger = get_logger("SkillClima")

def run(texto: str) -> str:
    try:
        logger.info(f"SkillClima ejecutado con input: {texto}")
        respuesta = "Hace 25°C y soleado"
        logger.debug(f"Resultado: {respuesta}")
        return respuesta
    except Exception:
        log_exception(logger, "Error ejecutando SkillClima")
        return "No pude ejecutar el skill"
