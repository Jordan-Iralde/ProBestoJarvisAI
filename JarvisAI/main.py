# main.py

import sys
from core.utils import (
    full_environment_diagnostic,
    get_logger,
    check_camera_available,
    check_microphone_available,
)
from interfaces.cli.interface import iniciar_cli
from interfaces.gui.app import iniciar_gui
from core.config_manager import ConfigManager
from core.terms import TermsManager

log = get_logger("main")

def choose_mode():
    """Decide CLI vs GUI según args o hardware."""
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        return modo == "cli"
    tiene_mic = check_microphone_available()
    tiene_cam = check_camera_available()
    return not (tiene_mic or tiene_cam)

if __name__ == "__main__":
    log.info("=== Iniciando JarvisAI ===")
    # 1. Términos de uso: mostrar y solicitar aceptación
    terms = TermsManager()
    if not terms.has_accepted():
        terms.prompt_acceptance()

    # 2. Diagnóstico del entorno
    diag = full_environment_diagnostic()
    log.info(f"Diagnóstico: {diag}")

    # 3. Cargar o inicializar configuración local
    config = ConfigManager().load_or_init()

    # 4. Elegir modo de interfaz
    usar_cli = choose_mode()
    if usar_cli:
        log.info("Usando modo CLI")
        iniciar_cli()
    else:
        log.info("Usando modo GUI")
        iniciar_gui()
