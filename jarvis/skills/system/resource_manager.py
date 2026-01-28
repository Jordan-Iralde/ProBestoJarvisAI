# skills/system/resource_manager.py
"""
Resource Manager - Control de recursos del PC
Permite a Jarvis monitorear y controlar procesos, memoria, CPU, disco
"""

import psutil
import os
import subprocess
from typing import Dict, List, Optional


class ResourceManager:
    """Gestiona recursos del sistema (procesos, memoria, CPU, disco)"""
    
    def __init__(self, core=None):
        self.core = core
        self.monitored_processes = {}
        self.cpu_threshold = 80  # %
        self.memory_threshold = 80  # %
        self.disk_threshold = 90  # %
    
    def get_system_status(self) -> Dict:
        """Obtiene estado completo del sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "processes_count": len(psutil.pids()),
            "uptime_seconds": self._get_uptime()
        }
    
    def _get_memory_info(self) -> Dict:
        """Memory usage details"""
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_mb": mem.used // (1024*1024),
            "available_mb": mem.available // (1024*1024),
            "total_mb": mem.total // (1024*1024),
            "status": "CRITICAL" if mem.percent > 90 else "WARNING" if mem.percent > 75 else "OK"
        }
    
    def _get_disk_info(self) -> Dict:
        """Disk space details"""
        disk = psutil.disk_usage('/')
        return {
            "percent": disk.percent,
            "used_gb": disk.used // (1024*1024*1024),
            "free_gb": disk.free // (1024*1024*1024),
            "total_gb": disk.total // (1024*1024*1024),
            "status": "CRITICAL" if disk.percent > 95 else "WARNING" if disk.percent > 80 else "OK"
        }
    
    def _get_uptime(self) -> int:
        """System uptime in seconds"""
        return int(time.time() - psutil.boot_time())
    
    def list_processes(self, sort_by="memory", limit=10) -> List[Dict]:
        """List top processes by CPU or memory"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu": proc.info['cpu_percent'],
                    "memory": proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by specified metric
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        else:
            processes.sort(key=lambda x: x['memory'], reverse=True)
        
        return processes[:limit]
    
    def kill_process(self, pid_or_name: str, force=False) -> Dict:
        """Kill a process by PID or name"""
        try:
            if isinstance(pid_or_name, str) and pid_or_name.isdigit():
                proc = psutil.Process(int(pid_or_name))
            else:
                # Find by name
                procs = psutil.process_iter(['pid', 'name'])
                proc = None
                for p in procs:
                    if p.info['name'].lower() == pid_or_name.lower():
                        proc = psutil.Process(p.info['pid'])
                        break
            
            if not proc:
                return {"success": False, "error": "Process not found"}
            
            if force:
                proc.kill()
            else:
                proc.terminate()
                proc.wait(timeout=5)
            
            return {"success": True, "message": f"Process {proc.name()} terminated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def optimize_system(self) -> Dict:
        """Perform system optimization"""
        results = {
            "killed_processes": [],
            "freed_memory_mb": 0,
            "status": "OK"
        }
        
        # Kill idle/zombie processes if memory > 85%
        mem_info = self._get_memory_info()
        if mem_info['percent'] > 85:
            # Kill low-priority processes
            low_priority = ['notepad', 'calc', 'mspaint']
            for proc_name in low_priority:
                result = self.kill_process(proc_name, force=False)
                if result['success']:
                    results['killed_processes'].append(proc_name)
            
            # Estimate freed memory
            mem_after = self._get_memory_info()
            results['freed_memory_mb'] = mem_info['used_mb'] - mem_after['used_mb']
            results['status'] = "OPTIMIZED"
        
        return results
    
    def set_process_priority(self, pid: int, priority: str) -> Dict:
        """Set process priority (high, normal, low)"""
        try:
            proc = psutil.Process(pid)
            priority_map = {
                "high": psutil.HIGH_PRIORITY_CLASS,
                "normal": psutil.NORMAL_PRIORITY_CLASS,
                "low": psutil.BELOW_NORMAL_PRIORITY_CLASS
            }
            
            proc.nice(priority_map.get(priority, psutil.NORMAL_PRIORITY_CLASS))
            return {"success": True, "message": f"Priority set to {priority}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def monitor_process(self, pid: int, threshold_cpu=50, threshold_memory=50) -> bool:
        """Start monitoring a process"""
        try:
            proc = psutil.Process(pid)
            self.monitored_processes[pid] = {
                "name": proc.name(),
                "threshold_cpu": threshold_cpu,
                "threshold_memory": threshold_memory,
                "alerts": []
            }
            return True
        except Exception:
            return False
    
    def get_monitored_alerts(self) -> List[Dict]:
        """Get alerts for monitored processes"""
        alerts = []
        
        for pid, config in self.monitored_processes.items():
            try:
                proc = psutil.Process(pid)
                cpu = proc.cpu_percent(interval=0.1)
                memory = proc.memory_percent()
                
                if cpu > config['threshold_cpu']:
                    alerts.append({
                        "type": "CPU",
                        "pid": pid,
                        "name": config['name'],
                        "value": cpu,
                        "threshold": config['threshold_cpu']
                    })
                
                if memory > config['threshold_memory']:
                    alerts.append({
                        "type": "MEMORY",
                        "pid": pid,
                        "name": config['name'],
                        "value": memory,
                        "threshold": config['threshold_memory']
                    })
            except psutil.NoSuchProcess:
                del self.monitored_processes[pid]
        
        return alerts


import time
