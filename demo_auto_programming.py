#!/usr/bin/env python3
"""
Ejemplo de Auto-Programación - Demostración de capacidades de auto-generación
Este script muestra cómo Jarvis puede generar automáticamente nuevos skills.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from system.core.engine import JarvisCore

def demo_auto_programming():
    """Demostración de auto-programación"""

    print("🚀 Demo: Auto-Programación de Jarvis")
    print("=" * 50)

    # Config básica
    config = {
        "data_collection": False,
        "tts": False,
        "workers": 2,
        "debug_nlu": True
    }

    try:
        # Inicializar Jarvis
        print("📦 Inicializando Jarvis...")
        core = JarvisCore(config)
        core.boot()
        print("✅ Jarvis listo")

        # Ejemplo 1: Generar un skill básico
        print("\n🎯 Ejemplo 1: Generar skill 'saludar_usuario'")
        requirement = """
        Crear un skill que salude al usuario de manera personalizada.
        El skill debe:
        - Saludar con 'Hola' o 'Buenos días' según la hora
        - Recordar el nombre del usuario si está disponible
        - Ofrecer ayuda básica
        """

        print(f"📝 Requerimiento: {requirement.strip()}")

        # Usar auto_programming para generar el skill
        result = core.skill_dispatcher.dispatch("auto_programming", "generate_skill", {
            "name": "saludar_usuario",
            "description": requirement,
            "category": "social"
        })

        if result and result.get("success"):
            print("✅ Skill generado exitosamente:")
            print(result["skill_code"])
        else:
            print("❌ Error generando skill:", result.get("error", "Unknown error"))

        # Ejemplo 2: Optimizar código existente
        print("\n🎯 Ejemplo 2: Optimizar código existente")

        sample_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Calcular fibonacci de 10
result = calculate_fibonacci(10)
print(f"Fibonacci de 10: {result}")
"""

        print("📝 Código original (ineficiente):")
        print(sample_code)

        result = core.skill_dispatcher.dispatch("auto_programming", "optimize", {
            "code": sample_code,
            "optimization_type": "performance"
        })

        if result and result.get("success"):
            print("✅ Código optimizado:")
            print(result["optimized_code"])
        else:
            print("❌ Error optimizando código:", result.get("error", "Unknown error"))

        # Ejemplo 3: Análisis del codebase
        print("\n🎯 Ejemplo 3: Análisis del codebase")

        result = core.skill_dispatcher.dispatch("auto_programming", "analyze")

        if result and result.get("success"):
            analysis = result["analysis"]
            print("✅ Análisis completado:")
            print(f"  📁 Total archivos: {analysis['total_files']}")
            print(f"  📊 Total líneas: {analysis['total_lines']}")
            print(f"  🛠️ Skills encontrados: {len(analysis['skills'])}")
            print(f"  🔧 Funciones: {analysis['functions_count']}")
            print(f"  📚 Clases: {analysis['classes_count']}")
        else:
            print("❌ Error en análisis:", result.get("error", "Unknown error"))

        # Ejemplo 4: Auto-optimización del sistema
        print("\n🎯 Ejemplo 4: Auto-optimización del sistema")

        result = core.skill_dispatcher.dispatch("system_auto_optimization", "full_optimization")

        if result and result.get("success"):
            opt = result["full_optimization"]
            print("✅ Optimización completada:")
            print(f"  ⏰ Timestamp: {opt['timestamp']}")
            print(f"  ✅ Operaciones exitosas: {opt['operations_completed']}/{opt['total_operations']}")
            print(f"  📋 Resumen: {opt['summary']}")
        else:
            print("❌ Error en optimización:", result.get("error", "Unknown error"))

        # Limpiar
        core.stop()
        print("\n🎉 Demo completada exitosamente")

    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_auto_programming()