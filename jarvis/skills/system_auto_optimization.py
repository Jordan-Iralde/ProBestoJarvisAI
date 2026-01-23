# skills/system_auto_optimization.py
"""
System Auto-Optimization Skill - Automatic system optimization capabilities
Implements auto-tuning, energy management, cleanup, and defragmentation.
"""

import os
import psutil
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import shutil
import subprocess


class SystemAutoOptimizationSkill:
    """
    Skill for automatic system optimization.
    Provides proactive system maintenance and resource management.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.last_optimization = None
        self.optimization_interval = 3600  # 1 hour
        self.temp_dirs = [
            os.environ.get('TEMP', 'C:\\Windows\\Temp'),
            os.environ.get('TMP', 'C:\\Windows\\Temp'),
            os.path.expanduser('~\\AppData\\Local\\Temp')
        ]

    def run(self, entities, core):
        """
        Execute auto-optimization commands.
        Commands: tune_resources, manage_energy, cleanup_temp, defrag_disk, full_optimization
        """
        # Extraer comando de entities
        command = entities.get("command", "analyze_system")

        try:
            if command == "tune_resources":
                return self._tune_resources()
            elif command == "manage_energy":
                return self._manage_energy()
            elif command == "cleanup_temp":
                return self._cleanup_temp()
            elif command == "defrag_disk":
                return self._defrag_disk()
            elif command == "full_optimization":
                return self._full_optimization()
            elif command == "analyze_system":
                return self._analyze_system_needs()
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}",
                    "available_commands": ["tune_resources", "manage_energy", "cleanup_temp", "defrag_disk", "full_optimization", "analyze_system"]
                }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Auto-optimization error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_system_needs(self) -> Dict[str, Any]:
        """Analyze current system state and determine optimization needs"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Calculate optimization priority
            needs = []

            if cpu_percent > 80:
                needs.append({"type": "cpu_tuning", "priority": "high", "description": "High CPU usage detected"})
            elif cpu_percent > 50:
                needs.append({"type": "cpu_tuning", "priority": "medium", "description": "Moderate CPU usage"})

            if memory.percent > 85:
                needs.append({"type": "memory_cleanup", "priority": "high", "description": "High memory usage"})
            elif memory.percent > 70:
                needs.append({"type": "memory_cleanup", "priority": "medium", "description": "Moderate memory usage"})

            if disk.percent > 90:
                needs.append({"type": "disk_cleanup", "priority": "high", "description": "Low disk space"})
            elif disk.percent > 75:
                needs.append({"type": "disk_cleanup", "priority": "medium", "description": "Moderate disk usage"})

            # Check temp files size
            temp_size = self._calculate_temp_size()
            if temp_size > 1024 * 1024 * 1024:  # > 1GB
                needs.append({"type": "temp_cleanup", "priority": "high", "description": f"Large temp files: {temp_size/1024/1024:.1f}MB"})

            return {
                "success": True,
                "analysis": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "temp_size_mb": temp_size / 1024 / 1024,
                    "needs": needs,
                    "recommendations": self._generate_recommendations(needs)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Analysis failed: {e}"}

    def _generate_recommendations(self, needs: List[Dict]) -> List[str]:
        """Generate optimization recommendations based on needs"""
        recommendations = []

        high_priority = [n for n in needs if n["priority"] == "high"]
        medium_priority = [n for n in needs if n["priority"] == "medium"]

        if high_priority:
            recommendations.append("🚨 High priority optimizations needed:")
            for need in high_priority:
                recommendations.append(f"  • {need['description']}")

        if medium_priority:
            recommendations.append("⚠️ Medium priority optimizations suggested:")
            for need in medium_priority:
                recommendations.append(f"  • {need['description']}")

        if not needs:
            recommendations.append("✅ System is well optimized")

        return recommendations

    def _tune_resources(self) -> Dict[str, Any]:
        """Auto-tune CPU and memory resources based on usage patterns"""
        try:
            # Get current usage
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()

            # Simple tuning logic (can be enhanced with ML)
            optimizations = []

            # CPU tuning
            if cpu_freq:
                current_freq = cpu_freq.current
                max_freq = cpu_freq.max
                if current_freq < max_freq * 0.7:
                    optimizations.append(f"CPU frequency: {current_freq:.0f}MHz (can increase to {max_freq:.0f}MHz)")

            # Memory optimization suggestions
            if memory.percent > 80:
                optimizations.append("High memory usage - consider closing unused applications")
            elif memory.percent < 30:
                optimizations.append("Memory usage low - system has capacity for more tasks")

            # Process optimization
            high_cpu_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:
                        high_cpu_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if high_cpu_processes:
                optimizations.append(f"High CPU processes: {len(high_cpu_processes)} detected")

            return {
                "success": True,
                "tuning": {
                    "cpu_cores": cpu_count,
                    "memory_total_gb": memory.total / 1024 / 1024 / 1024,
                    "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                    "optimizations": optimizations,
                    "recommendations": [
                        "Monitor CPU usage patterns for 24 hours",
                        "Consider process prioritization",
                        "Enable power management features"
                    ]
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Resource tuning failed: {e}"}

    def _manage_energy(self) -> Dict[str, Any]:
        """Intelligent energy management based on activity"""
        try:
            # Get power info
            battery = psutil.sensors_battery()
            is_plugged = battery.power_plugged if battery else True

            # Get activity level (simplified)
            cpu_percent = psutil.cpu_percent(interval=1)
            active_processes = len(list(psutil.process_iter()))

            # Determine energy mode
            if not is_plugged and battery:
                # On battery
                if cpu_percent < 20 and active_processes < 50:
                    mode = "power_saver"
                    recommendations = ["Switch to power saver mode", "Reduce screen brightness", "Disable unnecessary services"]
                else:
                    mode = "balanced"
                    recommendations = ["Use balanced power plan", "Monitor battery usage"]
            else:
                # Plugged in
                if cpu_percent > 70 or active_processes > 100:
                    mode = "high_performance"
                    recommendations = ["Switch to high performance mode", "Ensure cooling is adequate"]
                else:
                    mode = "balanced"
                    recommendations = ["Use balanced power plan", "Consider energy-saving features"]

            return {
                "success": True,
                "energy_management": {
                    "power_source": "plugged_in" if is_plugged else "battery",
                    "battery_percent": battery.percent if battery else None,
                    "current_mode": mode,
                    "activity_level": "high" if cpu_percent > 50 else "low",
                    "recommendations": recommendations
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Energy management failed: {e}"}

    def _cleanup_temp(self) -> Dict[str, Any]:
        """Clean temporary files and cache"""
        try:
            total_cleaned = 0
            cleaned_files = []

            for temp_dir in self.temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                file_size = os.path.getsize(file_path)

                                # Only delete files older than 1 day and larger than 1MB
                                if file_size > 1024 * 1024:
                                    file_age = time.time() - os.path.getmtime(file_path)
                                    if file_age > 86400:  # 24 hours
                                        os.remove(file_path)
                                        total_cleaned += file_size
                                        cleaned_files.append(file_path)
                            except (OSError, PermissionError):
                                continue

            return {
                "success": True,
                "cleanup": {
                    "total_cleaned_mb": total_cleaned / 1024 / 1024,
                    "files_cleaned": len(cleaned_files),
                    "directories_scanned": len(self.temp_dirs),
                    "message": f"Cleaned {len(cleaned_files)} temp files ({total_cleaned/1024/1024:.1f}MB)"
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Temp cleanup failed: {e}"}

    def _defrag_disk(self) -> Dict[str, Any]:
        """Intelligent disk defragmentation"""
        try:
            # Check if defrag is needed (simplified)
            disk = psutil.disk_usage('/')

            # Run Windows defrag (if available)
            try:
                result = subprocess.run(['defrag', '/C', '/U'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return {
                        "success": True,
                        "defrag": {
                            "disk_percent": disk.percent,
                            "defrag_output": result.stdout.strip(),
                            "message": "Disk defragmentation completed"
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Defrag failed: {result.stderr}"
                    }
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "Defrag tool not available on this system"
                }
        except Exception as e:
            return {"success": False, "error": f"Disk defrag failed: {e}"}

    def _full_optimization(self) -> Dict[str, Any]:
        """Run complete system optimization suite"""
        try:
            results = {}

            # Run all optimizations
            results["analysis"] = self._analyze_system_needs()
            results["tuning"] = self._tune_resources()
            results["energy"] = self._manage_energy()
            results["cleanup"] = self._cleanup_temp()

            # Attempt defrag (may fail on some systems)
            try:
                results["defrag"] = self._defrag_disk()
            except:
                results["defrag"] = {"success": False, "error": "Defrag not available"}

            # Calculate overall success
            successful_ops = sum(1 for r in results.values() if r.get("success", False))
            total_ops = len(results)

            self.last_optimization = datetime.now()

            return {
                "success": True,
                "full_optimization": {
                    "timestamp": self.last_optimization.isoformat(),
                    "operations_completed": successful_ops,
                    "total_operations": total_ops,
                    "results": results,
                    "summary": f"Completed {successful_ops}/{total_ops} optimization operations"
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Full optimization failed: {e}"}

    def _calculate_temp_size(self) -> int:
        """Calculate total size of temp files"""
        total_size = 0
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except (OSError, PermissionError):
                            continue
        return total_size