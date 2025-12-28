# actions/dispatcher.py

class SkillDispatcher:
    def __init__(self):
        # Usar un solo registro para evitar duplicación
        self.skills = {}  # Este es el que usa NLUPipeline

    def register(self, intent_name, skill_cls):
        """
        Registra una skill para un intent específico.
        
        Args:
            intent_name (str): Nombre del intent (ej: "open_app")
            skill_cls (class): Clase de la skill (no instancia)
        """
        self.skills[intent_name] = skill_cls
        print(f"[DISPATCHER] Registered skill: {intent_name}")

    def dispatch(self, intent, entities, system_state):
        """
        Ejecuta la skill correspondiente al intent.
        
        Args:
            intent (str): Intent detectado
            entities (dict): Entidades extraídas
            system_state: Estado del sistema
            
        Returns:
            dict: Resultado de la ejecución
        """
        if intent not in self.skills:
            print(f"[DISPATCHER] ⚠ Intent '{intent}' no tiene skill registrada")
            return {
                "success": False,
                "error": f"skill_not_implemented:{intent}",
                "available_skills": list(self.skills.keys())
            }

        try:
            # Instanciar y ejecutar la skill
            skill_cls = self.skills[intent]
            skill_instance = skill_cls()
            
            print(f"[DISPATCHER] ▶ Executing skill: {intent}")
            result = skill_instance.run(entities, system_state)
            
            return {
                "success": True,
                "intent": intent,
                "result": result
            }
            
        except Exception as e:
            print(f"[DISPATCHER] ✗ Error ejecutando {intent}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "intent": intent
            }

    def list_skills(self):
        """Retorna lista de skills disponibles"""
        return list(self.skills.keys())

    def get_skill_info(self, intent_name):
        """Obtiene información sobre una skill"""
        if intent_name not in self.skills:
            return None
        
        skill_cls = self.skills[intent_name]
        return {
            "name": intent_name,
            "class": skill_cls.__name__,
            "doc": skill_cls.__doc__ or "Sin documentación"
        }