#!/usr/bin/env python3
import sys

TEMPLATE = """# Tipo de commit:
# feat     - nueva funcionalidad
# fix      - corrección de error
# chore    - mantenimiento general
# docs     - documentación
# refactor - cambio interno sin afectar funcionalidad
# test     - pruebas
# style    - formato, espacios, nombres
# ci       - integración continua
#
# Ejemplos:
# 🧠 feat(utils): diagnóstico completo del sistema
# 🛠 chore(config): ajustes en paths y entorno
# 📄 docs: agregado manifiesto ético
"""

def main():
    if len(sys.argv) < 2:
        return
    msg_path = sys.argv[1]
    with open(msg_path, 'r+') as f:
        content = f.read()
        if not content.strip():
            f.write(TEMPLATE)
        else:
            f.seek(0)
            f.write(content + '\n' + TEMPLATE)

if __name__ == "__main__":
    main()
