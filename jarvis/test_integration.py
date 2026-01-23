#!/usr/bin/env python3
"""
Script de prueba para verificar que Jarvis inicia correctamente
"""

import sys
import os
import time
import threading

sys.path.append(os.path.dirname(__file__))

from system.core.engine import JarvisCore

def test_jarvis_boot():
    """Probar que Jarvis inicia correctamente"""

    print("🚀 Probando inicialización de Jarvis...")

    # Config básica
    config = {
        "name": "Jarvis",
        "version": "0.0.3",
        "author": "Jordan",
        "data_collection": False,
        "tts": False,
        "workers": 2,
        "debug_nlu": True,
        "web_dashboard": False,  # Deshabilitar dashboard para pruebas
        "ask_consent": False,
        "log_level": "DEBUG"  # Habilitar debug
    }

    core = None
    try:
        print("📦 Inicializando JarvisCore...")
        core = JarvisCore(config)

        print("🔄 Ejecutando boot sequence...")
        core.boot()
        print("✅ Boot completado exitosamente")

        # Verificar componentes críticos
        checks = {
            "Input adapter": hasattr(core, 'input') and core.input is not None,
            "NLU pipeline": hasattr(core, 'nlu') and core.nlu is not None,
            "Skill dispatcher": hasattr(core, 'skill_dispatcher') and len(core.skill_dispatcher.skills) > 0,
            "Storage": hasattr(core, 'storage') and core.storage is not None,
            "Active learning": hasattr(core, 'active_learning') and core.active_learning is not None,
        }

        print("\n🔍 Verificando componentes:")
        all_good = True
        for component, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component}: {'OK' if status else 'FALLANDO'}")
            if not status:
                all_good = False

        if all_good:
            print("\n🎉 Todos los componentes inicializados correctamente")
            print(f"📊 Skills registrados: {len(core.skill_dispatcher.skills)}")

            # Mostrar algunos skills
            skills = list(core.skill_dispatcher.skills.keys())[:5]
            print(f"🛠️ Primeros skills: {', '.join(skills)}")

            return True
        else:
            print("\n❌ Algunos componentes fallaron")
            return False

    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if core:
            try:
                core.stop()
                print("🛑 Jarvis detenido correctamente")
            except:
                pass

def test_basic_commands():
    """Probar algunos comandos básicos"""

    print("\n🎯 Probando comandos básicos...")

    config = {
        "name": "Jarvis",
        "version": "0.0.3",
        "author": "Jordan",
        "data_collection": False,
        "tts": False,
        "workers": 2,
        "debug_nlu": False,
        "web_dashboard": False,
        "ask_consent": False,
        "log_level": "DEBUG"
    }

    core = None
    try:
        core = JarvisCore(config)
        core.boot()

        # Probar comando de estado del sistema
        print("📊 Probando comando 'system_status'...")
        result = core.skill_dispatcher.dispatch("system_status", {}, core)
        if result and result.get("success"):
            print("✅ Comando system_status: OK")
        else:
            print("❌ Comando system_status: FALLANDO")

        # Probar auto-optimización
        print("🔧 Probando comando 'system_auto_optimization'...")
        result = core.skill_dispatcher.dispatch("system_auto_optimization", {"command": "analyze_system"}, core)
        if result and result.get("success"):
            print("✅ Comando system_auto_optimization: OK")
        else:
            print("❌ Comando system_auto_optimization: FALLANDO")

        return True

    except Exception as e:
        print(f"❌ Error probando comandos: {e}")
        return False

    finally:
        if core:
            try:
                core.stop()
            except:
                pass

if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS - Suite de Pruebas de Integración")
    print("=" * 60)

    # Prueba 1: Inicialización
    boot_success = test_jarvis_boot()

    # Prueba 2: Comandos básicos (solo si boot fue exitoso)
    commands_success = False
    if boot_success:
        commands_success = test_basic_commands()

    # Resultado final
    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL:")
    print(f"  Boot: {'✅ PASÓ' if boot_success else '❌ FALLÓ'}")
    print(f"  Comandos: {'✅ PASÓ' if commands_success else '❌ FALLÓ'}")

    if boot_success and commands_success:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - LISTO PARA COMMIT")
        sys.exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - REVISAR ERRORES")
        sys.exit(1)