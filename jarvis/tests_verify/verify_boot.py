#!/usr/bin/env python3
"""Verificar que Jarvis carga sin errores de importación."""

import sys
import json
import os

def test_boot():
    """Test boot sequence."""
    print("\n" + "="*60)
    print("✓ Verificación de Jarvis v0.0.4")
    print("="*60 + "\n")
    
    try:
        # Cargar config
        print("[1/2] Cargando configuración...")
        base = os.path.dirname(__file__)
        config_path = os.path.join(base, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"✓ Config cargada (version: {config.get('version', '?')})\n")
        
        # Importar JarvisCore
        print("[2/2] Importando JarvisCore...")
        from system.core.engine import JarvisCore
        print("✓ Importación exitosa (sin errores de módulos)\n")
        
        # Crear instancia
        print("[3/3] Inicializando JarvisCore...")
        core = JarvisCore(config)
        print(f"✓ JarvisCore creado\n")
        
        # Boot
        print("[4/3] Ejecutando boot...")
        core.boot()
        print(f"✓ Boot completado\n")
        
        # Mostrar status
        status = core.get_system_status()
        print(f"Status: {status}\n")
        
        # Skills
        skills = core.get_available_skills()
        print(f"✓ {len(skills)} skills cargados\n")
        
        # Cleanup
        core.stop()
        
        print("="*60)
        print("✅ JARVIS LISTO PARA USAR")
        print("="*60)
        print("\n🚀 Ejecuta: python main.py\n")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boot()
    sys.exit(0 if success else 1)
