import sys
import threading
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
from modules.datos.recoleccion import iniciar_recoleccion_datos
from config.settings import config as settings_config  # Importa el singleton real

log = get_logger("main")

def choose_mode():
    """Decide CLI vs GUI según args o hardware."""
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        return modo == "cli"
    return not (check_microphone_available() or check_camera_available())

if __name__ == "__main__":
    log.info("=== Iniciando JarvisAI ===")

    # 1. Aceptación de términos
    terms = TermsManager()
    if not terms.has_accepted():
        terms.prompt_acceptance()

    # 2. Diagnóstico inicial
    diag = full_environment_diagnostic()
    log.info(f"Diagnóstico: {diag}")

    # 3. Configuración local
    local_config = ConfigManager().load_or_init()

    # 4. Recolección de datos en segundo plano
    if settings_config.dc_enabled:
        threading.Thread(target=iniciar_recoleccion_datos, args=(settings_config,), daemon=True).start()
        log.info("✔️ Recolección de datos activada")

    # 5. Interfaz
    usar_cli = choose_mode()
    if usar_cli:
        log.info("Usando modo CLI")
        iniciar_cli()
    else:
        log.info("Usando modo GUI")
        iniciar_gui()
