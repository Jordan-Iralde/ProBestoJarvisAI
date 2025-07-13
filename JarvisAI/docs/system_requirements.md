# Requisitos del Sistema para JarvisAI

## Python
- Python 3.8+  
- **Tkinter** (GUI):
  - **Windows**: incluído por defecto si instalaste con “tcl/tk and IDLE”.
  - **Debian/Ubuntu**: `sudo apt install python3-tk`
  - **Fedora**: `sudo dnf install python3-tkinter`
  - **Arch**: `sudo pacman -S tk`

## Otros sistemas
- En macOS: viene con Python oficial de python.org, si usás Homebrew puede faltar: `brew install python-tk`.
- Asegurate de tener **Microphone drivers** y **cámara** funcionando en el sistema.

## Cómo usar
1. Instalá las dependencias del sistema.
2. Corré el script de instalación:
   ```bash
   chmod +x scripts/install_dependencies.sh
   ./scripts/install_dependencies.sh
