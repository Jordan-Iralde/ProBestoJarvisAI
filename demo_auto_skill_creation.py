#!/usr/bin/env python3
"""
Ejemplo: Auto-Implementación de Skills
Demuestra cómo Jarvis puede crear y registrar nuevos skills automáticamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from system.core.engine import JarvisCore

def demo_auto_skill_creation():
    """Demostración de creación automática de skills"""

    print("🚀 Demo: Auto-Implementación de Skills")
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

        # Paso 1: Generar código del skill usando auto_programming
        print("\n🎯 Paso 1: Generar código del skill 'calculadora_avanzada'")

        requirement = """
        Crear un skill de calculadora avanzada que pueda:
        - Realizar operaciones básicas (+, -, *, /)
        - Calcular funciones matemáticas (sqrt, pow, sin, cos, tan)
        - Resolver ecuaciones simples
        - Convertir unidades (metros a pies, celsius a fahrenheit)
        - Calcular porcentajes y descuentos
        """

        print(f"📝 Requerimiento: {requirement.strip()}")

        result = core.skill_dispatcher.dispatch("auto_programming", "generate_skill", {
            "name": "calculadora_avanzada",
            "description": requirement,
            "category": "matematica"
        })

        if result and result.get("success"):
            skill_code = result["skill_code"]
            print("✅ Código generado exitosamente")
            print("\n" + "="*50)
            print("CÓDIGO GENERADO:")
            print("="*50)
            print(skill_code)
            print("="*50)

            # Paso 2: Crear el archivo del skill
            print("\n🎯 Paso 2: Crear archivo del skill")

            skill_filename = "skills/calculadora_avanzada.py"
            with open(skill_filename, 'w', encoding='utf-8') as f:
                f.write(skill_code)

            print(f"✅ Archivo creado: {skill_filename}")

            # Paso 3: Intentar importar y registrar el skill dinámicamente
            print("\n🎯 Paso 3: Registrar skill dinámicamente")

            try:
                # Importar el módulo dinámicamente
                import importlib.util
                spec = importlib.util.spec_from_file_location("calculadora_avanzada", skill_filename)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Obtener la clase del skill
                skill_class = getattr(module, 'CalculadoraAvanzadaSkill')

                # Registrar en el dispatcher
                core.skill_dispatcher.register("calculadora_avanzada", skill_class())

                print("✅ Skill registrado dinámicamente")
                print(f"🛠️ Skills totales ahora: {len(core.skill_dispatcher.skills)}")

                # Paso 4: Probar el skill
                print("\n🎯 Paso 4: Probar el skill generado")

                test_commands = [
                    ("calculate", {"expression": "2 + 3 * 4"}),
                    ("sqrt", {"value": 16}),
                    ("convert", {"from_unit": "celsius", "to_unit": "fahrenheit", "value": 25})
                ]

                for cmd, params in test_commands:
                    try:
                        result = core.skill_dispatcher.dispatch("calculadora_avanzada", cmd, params)
                        if result and result.get("success"):
                            print(f"✅ {cmd}({params}): {result}")
                        else:
                            print(f"❌ {cmd}({params}): {result.get('error', 'Error desconocido')}")
                    except Exception as e:
                        print(f"❌ Error ejecutando {cmd}: {e}")

            except Exception as e:
                print(f"❌ Error registrando skill: {e}")
                print("💡 El skill fue generado pero necesita revisión manual")

        else:
            print("❌ Error generando skill:", result.get("error", "Unknown error"))

        # Paso 5: Mostrar skills disponibles
        print("\n🎯 Paso 5: Skills disponibles después de la creación")
        skills = list(core.skill_dispatcher.skills.keys())
        print(f"📚 Total skills: {len(skills)}")
        for skill in sorted(skills):
            print(f"  • {skill}")

        # Limpiar
        core.stop()
        print("\n🎉 Demo completada exitosamente")

    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

def demo_skill_templates():
    """Mostrar templates disponibles para generación de skills"""

    print("\n🔧 Templates de Skills Disponibles:")
    print("=" * 40)

    templates = {
        "social": "Skills para interacción social (saludos, conversación)",
        "matematica": "Skills de cálculo y matemáticas",
        "sistema": "Skills de gestión del sistema operativo",
        "productividad": "Skills para organización y tareas",
        "entretenimiento": "Skills de juegos y diversión",
        "utilidades": "Skills de herramientas generales",
        "inteligencia": "Skills de IA y aprendizaje",
        "automatizacion": "Skills para automatización de tareas"
    }

    for category, description in templates.items():
        print(f"📁 {category}: {description}")

    print("\n💡 Para generar un skill, usa:")
    print("   auto_programming generate_skill nombre_skill descripción categoría")

if __name__ == "__main__":
    demo_auto_skill_creation()
    demo_skill_templates()