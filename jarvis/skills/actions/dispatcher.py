# actions/dispatcher.py
import inspect

class SkillDispatcher:
    def __init__(self, logger=None):
        # Usar un solo registro para evitar duplicación
        self.skills = {}  # Este es el que usa NLUPipeline
        self.logger = logger

    def _log(self, level: str, msg: str):
        if self.logger:
            fn = getattr(self.logger, level, None)
            if callable(fn):
                fn(msg)
                return
        # fallback
        print(msg)

    def register(self, intent_name, skill_cls):
        """
        Registra una skill para un intent específico.
        
        Args:
            intent_name (str): Nombre del intent (ej: "open_app")
            skill_cls (class): Clase de la skill (no instancia)
        """
        self.skills[intent_name] = skill_cls
        self._log("debug", f"[DISPATCHER] Registered skill: {intent_name}")

    def dispatch(self, intent, entities, core):
        """
        Ejecuta la skill correspondiente al intent.
        
        Args:
            intent (str): Intent detectado
            entities (dict): Entidades extraídas
            core: Instancia del JarvisCore
            
        Returns:
            dict: Resultado de la ejecución
        """
        if intent not in self.skills:
            self._log("warning", f"[DISPATCHER] Intent '{intent}' no tiene skill registrada")
            return {
                "success": False,
                "error": f"skill_not_implemented:{intent}",
                "available_skills": list(self.skills.keys())
            }

        try:
            # Instanciar y ejecutar la skill
            skill_cls = self.skills[intent]

            # Verificar si es una clase o ya es una instancia
            if inspect.isclass(skill_cls):
                # Es una clase, instanciar
                skill_instance = skill_cls()
                self._log("debug", f"[DISPATCHER] Created new instance for {intent}")
            else:
                # Ya es una instancia
                skill_instance = skill_cls
                self._log("debug", f"[DISPATCHER] Using existing instance for {intent}")

            self._log("info", f"[DISPATCHER] Executing skill: {intent}")
            self._log("debug", f"[DISPATCHER] Calling run with entities={entities}, core={type(core)}")
            result = skill_instance.run(entities, core)

            return {
                "success": True,
                "intent": intent,
                "result": result
            }
            
        except Exception as e:
            self._log("error", f"[DISPATCHER] Error ejecutando {intent}: {e}")
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