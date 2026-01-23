# skills/analyze_system_health.py
"""
Analyze System Health Skill - PC monitoring and optimization recommendations
Monitors system resources and provides health analysis and recommendations.
"""

import psutil
import platform
import time
from typing import Dict, Any, List
import os


class AnalyzeSystemHealthSkill:
    """
    Skill for analyzing system health, resource usage, and providing optimization recommendations.
    Never executes changes automatically - only provides analysis and suggestions.
    """

    def __init__(self, logger=None):
        self.logger = logger

    def run(self, focus_area: str = "general") -> Dict[str, Any]:
        """
        Analyze system health and provide recommendations.

        Args:
            focus_area: Area to focus on ("cpu", "memory", "disk", "network", "general")

        Returns:
            Comprehensive system health analysis
        """
        try:
            analysis = {
                "timestamp": time.time(),
                "system_info": self._get_system_info(),
                "health_score": 0,
                "issues": [],
                "recommendations": [],
                "resource_usage": {},
                "performance_metrics": {}
            }

            # Gather resource usage
            analysis["resource_usage"] = self._analyze_resource_usage()

            # Analyze specific focus area
            if focus_area == "cpu":
                analysis.update(self._analyze_cpu_health())
            elif focus_area == "memory":
                analysis.update(self._analyze_memory_health())
            elif focus_area == "disk":
                analysis.update(self._analyze_disk_health())
            elif focus_area == "network":
                analysis.update(self._analyze_network_health())
            else:
                # General analysis
                analysis.update(self._analyze_general_health())

            # Calculate overall health score
            analysis["health_score"] = self._calculate_health_score(analysis)

            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)

            return {
                "success": True,
                "analysis": analysis,
                "focus_area": focus_area
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analizando salud del sistema: {str(e)}",
                "focus_area": focus_area
            }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        }

    def _analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze current resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": self._get_network_usage()
        }

    def _get_network_usage(self) -> Dict[str, Any]:
        """Get network usage statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {"error": "No se pudo obtener información de red"}

    def _analyze_cpu_health(self) -> Dict[str, Any]:
        """Analyze CPU health specifically"""
        issues = []
        metrics = {}

        cpu_percent = psutil.cpu_percent(interval=1)
        metrics["cpu_usage"] = cpu_percent

        if cpu_percent > 90:
            issues.append({
                "type": "cpu",
                "severity": "high",
                "description": f"Uso de CPU extremadamente alto: {cpu_percent}%",
                "impact": "Puede causar lentitud general del sistema"
            })
        elif cpu_percent > 70:
            issues.append({
                "type": "cpu",
                "severity": "medium",
                "description": f"Uso de CPU elevado: {cpu_percent}%",
                "impact": "Puede afectar rendimiento de aplicaciones"
            })

        # Check CPU frequency if available
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                metrics["cpu_freq_current"] = cpu_freq.current
                metrics["cpu_freq_max"] = cpu_freq.max
        except:
            pass

        return {"cpu_issues": issues, "cpu_metrics": metrics}

    def _analyze_memory_health(self) -> Dict[str, Any]:
        """Analyze memory health specifically"""
        issues = []
        metrics = {}

        mem = psutil.virtual_memory()
        metrics["memory_usage"] = mem.percent

        if mem.percent > 90:
            issues.append({
                "type": "memory",
                "severity": "high",
                "description": f"Memoria casi llena: {mem.percent}% usado",
                "impact": "Puede causar swapping y lentitud extrema"
            })
        elif mem.percent > 80:
            issues.append({
                "type": "memory",
                "severity": "medium",
                "description": f"Memoria altamente utilizada: {mem.percent}% usado",
                "impact": "Puede afectar multitarea y aplicaciones grandes"
            })

        return {"memory_issues": issues, "memory_metrics": metrics}

    def _analyze_disk_health(self) -> Dict[str, Any]:
        """Analyze disk health specifically"""
        issues = []
        metrics = {}

        disk = psutil.disk_usage('/')
        metrics["disk_usage"] = disk.percent

        if disk.percent > 95:
            issues.append({
                "type": "disk",
                "severity": "high",
                "description": f"Disco casi lleno: {disk.percent}% usado",
                "impact": "Puede impedir instalación de software y actualizaciones"
            })
        elif disk.percent > 85:
            issues.append({
                "type": "disk",
                "severity": "medium",
                "description": f"Disco altamente utilizado: {disk.percent}% usado",
                "impact": "Limitado espacio para archivos temporales"
            })

        return {"disk_issues": issues, "disk_metrics": metrics}

    def _analyze_network_health(self) -> Dict[str, Any]:
        """Analyze network health specifically"""
        issues = []
        metrics = {}

        try:
            net_io = psutil.net_io_counters()
            metrics["network_io"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            }

            # Basic network health check
            issues.append({
                "type": "network",
                "severity": "info",
                "description": f"Tráfico de red: {net_io.bytes_sent} bytes enviados, {net_io.bytes_recv} bytes recibidos",
                "impact": "Información básica de uso de red"
            })

        except Exception as e:
            issues.append({
                "type": "network",
                "severity": "low",
                "description": f"Error obteniendo métricas de red: {str(e)}",
                "impact": "No se puede monitorear uso de red"
            })

        return {"network_issues": issues, "network_metrics": metrics}

    def _analyze_general_health(self) -> Dict[str, Any]:
        """Perform general system health analysis"""
        issues = []

        # Combine all resource analyses
        cpu_analysis = self._analyze_cpu_health()
        memory_analysis = self._analyze_memory_health()
        disk_analysis = self._analyze_disk_health()

        issues.extend(cpu_analysis.get("cpu_issues", []))
        issues.extend(memory_analysis.get("memory_issues", []))
        issues.extend(disk_analysis.get("disk_issues", []))

        # Check for high resource processes
        high_cpu_processes = self._get_high_resource_processes("cpu")
        high_memory_processes = self._get_high_resource_processes("memory")

        if high_cpu_processes:
            issues.append({
                "type": "processes",
                "severity": "medium",
                "description": f"Procesos con alto uso de CPU: {', '.join(high_cpu_processes[:3])}",
                "impact": "Pueden estar afectando rendimiento general"
            })

        if high_memory_processes:
            issues.append({
                "type": "processes",
                "severity": "medium",
                "description": f"Procesos con alto uso de memoria: {', '.join(high_memory_processes[:3])}",
                "impact": "Pueden estar causando presión de memoria"
            })

        return {
            "general_issues": issues,
            "high_cpu_processes": high_cpu_processes,
            "high_memory_processes": high_memory_processes
        }

    def _get_high_resource_processes(self, resource_type: str) -> List[str]:
        """Get processes with high resource usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if resource_type == "cpu" and proc.info['cpu_percent'] > 10:
                        processes.append(f"{proc.info['name']} ({proc.info['cpu_percent']}%)")
                    elif resource_type == "memory" and proc.info['memory_percent'] > 5:
                        processes.append(f"{proc.info['name']} ({proc.info['memory_percent']}%)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return processes[:5]  # Top 5
        except:
            return []

    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        base_score = 100

        # Penalize for each issue based on severity
        issues = analysis.get("issues", [])
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            elif severity == "low":
                base_score -= 5

        # Resource usage penalties
        resources = analysis.get("resource_usage", {})
        if resources.get("cpu_percent", 0) > 80:
            base_score -= 15
        if resources.get("memory", {}).get("percent", 0) > 85:
            base_score -= 15
        if resources.get("disk", {}).get("percent", 0) > 90:
            base_score -= 15

        return max(0, min(100, base_score))

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        issues = analysis.get("issues", [])
        health_score = analysis.get("health_score", 100)

        # General recommendations based on health score
        if health_score < 50:
            recommendations.append({
                "priority": "high",
                "action": "Revisar y resolver problemas críticos del sistema",
                "description": "Múltiples problemas detectados que afectan rendimiento",
                "risk": "high",
                "effort": "high"
            })
        elif health_score < 70:
            recommendations.append({
                "priority": "medium",
                "action": "Optimizar recursos del sistema",
                "description": "Problemas moderados que pueden mejorarse",
                "risk": "medium",
                "effort": "medium"
            })

        # Specific recommendations based on issues
        for issue in issues:
            if "CPU" in issue["description"] or "cpu" in issue["description"]:
                recommendations.append({
                    "priority": "medium",
                    "action": "Monitorear y gestionar procesos con alto uso de CPU",
                    "description": "Identificar aplicaciones que consumen excesivos recursos",
                    "risk": "medium",
                    "effort": "low"
                })
            elif "memoria" in issue["description"].lower():
                recommendations.append({
                    "priority": "medium",
                    "action": "Liberar memoria cerrando aplicaciones innecesarias",
                    "description": "Cerrar pestañas del navegador y aplicaciones no utilizadas",
                    "risk": "low",
                    "effort": "low"
                })
            elif "disco" in issue["description"].lower():
                recommendations.append({
                    "priority": "medium",
                    "action": "Liberar espacio en disco",
                    "description": "Eliminar archivos temporales y programas no utilizados",
                    "risk": "low",
                    "effort": "medium"
                })

        # Preventive recommendations
        if not issues:
            recommendations.append({
                "priority": "low",
                "action": "Mantener monitoreo regular del sistema",
                "description": "Sistema funcionando correctamente",
                "risk": "low",
                "effort": "low"
            })

        return recommendations[:5]  # Limit to top 5 recommendations