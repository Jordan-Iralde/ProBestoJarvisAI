# skills/system/manage_resources.py
"""
Skill para gestionar recursos del sistema
Permite a Jarvis monitorear y optimizar el PC
"""

from skills.actions.base.skill import Skill
from skills.system.resource_manager import ResourceManager


class ManageResourcesSkill(Skill):
    """Manage system resources (processes, memory, CPU)"""
    
    patterns = [
        r".*recurso.*",
        r".*memoria.*",
        r".*cpu.*",
        r".*proces.*",
        r".*optimiz.*",
        r".*limpiar.*"
    ]
    
    def __init__(self):
        super().__init__()
        self.name = "manage_resources"
        self.description = "Monitorea y gestiona recursos del PC"
        self.resource_mgr = ResourceManager()
    
    def run(self, entities, core=None):
        """Execute resource management"""
        
        # Determine action from entities
        action = entities.get("action", ["status"])[0] if entities.get("action") else "status"
        
        if action in ["estado", "status", "info"]:
            return self._show_status()
        elif action in ["procesos", "processes", "apps"]:
            return self._list_processes(entities)
        elif action in ["optimizar", "optimize", "limpiar", "cleanup"]:
            return self._optimize()
        elif action in ["matar", "kill", "terminar"]:
            return self._kill_process(entities)
        else:
            return self._show_status()
    
    def _show_status(self):
        """Show system status"""
        status = self.resource_mgr.get_system_status()
        
        cpu = status["cpu_percent"]
        mem = status["memory"]
        disk = status["disk"]
        
        message = f"""
        [SYSTEM STATUS]
        CPU: {cpu:.1f}%
        Memory: {mem['percent']:.1f}% ({mem['used_mb']}MB/{mem['total_mb']}MB) - {mem['status']}
        Disk: {disk['percent']:.1f}% ({disk['used_gb']}GB/{disk['total_gb']}GB) - {disk['status']}
        Processes: {status['processes_count']}
        """.strip()
        
        return {
            "success": True,
            "result": message,
            "data": status
        }
    
    def _list_processes(self, entities):
        """List top processes"""
        limit = 10
        if entities.get("number"):
            limit = int(entities.get("number")[0])
        
        sort_by = "memory"
        if "cpu" in str(entities):
            sort_by = "cpu"
        
        processes = self.resource_mgr.list_processes(sort_by=sort_by, limit=limit)
        
        message = f"Top {limit} procesos por {sort_by.upper()}:\n"
        for p in processes:
            message += f"  {p['name']:<20} CPU:{p['cpu']:>5.1f}% MEM:{p['memory']:>5.1f}%\n"
        
        return {
            "success": True,
            "result": message,
            "processes": processes
        }
    
    def _optimize(self):
        """Optimize system"""
        result = self.resource_mgr.optimize_system()
        
        message = f"Optimización completada:\n"
        message += f"  Procesos terminados: {len(result['killed_processes'])}\n"
        message += f"  Memoria liberada: {result['freed_memory_mb']}MB\n"
        message += f"  Estado: {result['status']}"
        
        return {
            "success": True,
            "result": message,
            "optimization": result
        }
    
    def _kill_process(self, entities):
        """Kill a specific process"""
        if not entities.get("process_name"):
            return {"success": False, "error": "Debe especificar qué proceso terminar"}
        
        proc_name = entities.get("process_name")[0]
        result = self.resource_mgr.kill_process(proc_name, force=False)
        
        return {
            "success": result["success"],
            "result": result.get("message") or result.get("error")
        }
