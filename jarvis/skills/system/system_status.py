# actions/skills/system_status.py
import psutil
import platform


class SystemStatusSkill:
    """Muestra información del sistema"""
    
    patterns = [
        r"\b(estado|status|info|información)\b.*\b(sistema|system|pc|computadora)\b",
        r"\b(cpu|memoria|ram|disco)\b"
    ]
    
    def run(self, entities, core):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memoria
            mem = psutil.virtual_memory()
            mem_total = mem.total / (1024**3)  # GB
            mem_used = mem.used / (1024**3)
            mem_percent = mem.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)
            disk_used = disk.used / (1024**3)
            disk_percent = disk.percent
            
            return {
                "os": f"{platform.system()} {platform.release()}",
                "cpu": {"percent": cpu_percent, "cores": cpu_count},
                "memory": {"used_gb": mem_used, "total_gb": mem_total, "percent": mem_percent},
                "disk": {"used_gb": disk_used, "total_gb": disk_total, "percent": disk_percent}
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
