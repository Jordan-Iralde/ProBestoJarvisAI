#!/usr/bin/env python3
"""
Verificación final del proyecto Jarvis
"""

import os

def main():
    print('🚀 Verificando archivos del proyecto...')

    # Verificar que los archivos existen
    files_to_check = [
        'jarvis/system/core/engine.py',
        'jarvis/interface/text/input_adapter.py',
        'jarvis/skills/auto_programming.py',
        'innovation_roadmap.md'
    ]

    for file in files_to_check:
        if os.path.exists(file):
            print(f'✅ {file} existe')
        else:
            print(f'❌ {file} NO existe')

    print('\n🎯 Verificando contenido de archivos clave...')

    # Verificar que las mejoras están en input_adapter.py
    try:
        with open('jarvis/interface/text/input_adapter.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'def _show_help(self):' in content and 'def _show_status(self):' in content:
                print('✅ Interfaz CLI mejorada implementada')
            else:
                print('❌ Interfaz CLI no mejorada')
    except Exception as e:
        print(f'❌ Error leyendo input_adapter.py: {e}')

    # Verificar roadmap
    try:
        with open('innovation_roadmap.md', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Auto-Evolución' in content and 'Control Total del Ecosistema' in content:
                print('✅ Roadmap de innovación creado')
            else:
                print('❌ Roadmap incompleto')
    except Exception as e:
        print(f'❌ Error leyendo roadmap: {e}')

    print('\n✅ Verificación completada')

if __name__ == "__main__":
    main()