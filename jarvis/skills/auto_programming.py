# skills/auto_programming.py
"""
Auto Programming Skill - Jarvis self-modification capabilities
Allows Jarvis to generate, modify, and optimize its own code and configuration.
"""

import os
import re
from typing import Dict, Any, List
from datetime import datetime


class AutoProgrammingSkill:
    """
    Skill for self-programming capabilities.
    Allows Jarvis to analyze, generate, and modify its own code safely.
    """

    def __init__(self, storage=None, active_learning=None, logger=None):
        self.storage = storage
        self.active_learning = active_learning
        self.logger = logger
        self.jarvis_root = self._find_jarvis_root()

    def run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute auto-programming commands.

        Args:
            command: The programming command ("analyze", "generate_skill", "optimize", "diagnose")
            **kwargs: Additional parameters for the command

        Returns:
            Result of the auto-programming operation
        """
        try:
            if command == "analyze":
                return self._analyze_codebase()
            elif command == "generate_skill":
                return self._generate_skill(kwargs.get("skill_name", ""), kwargs.get("description", ""))
            elif command == "optimize":
                return self._optimize_codebase()
            elif command == "diagnose":
                return self._diagnose_issues()
            elif command == "create_config":
                return self._create_configuration(kwargs.get("config_type", ""))
            else:
                return {
                    "success": False,
                    "error": f"Comando desconocido: {command}",
                    "available_commands": ["analyze", "generate_skill", "optimize", "diagnose", "create_config"]
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en auto-programación: {str(e)}",
                "command": command
            }

    def _find_jarvis_root(self) -> str:
        """Find the Jarvis root directory"""
        current = os.path.dirname(os.path.abspath(__file__))
        # Go up until we find the jarvis directory
        while current and os.path.basename(current) != 'jarvis':
            current = os.path.dirname(current)
        return current or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the current codebase structure and health"""
        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "skills_count": 0,
            "test_coverage": 0,
            "issues": [],
            "recommendations": []
        }

        try:
            for root, dirs, files in os.walk(self.jarvis_root):
                for file in files:
                    if file.endswith(('.py', '.js', '.html', '.css', '.md')):
                        filepath = os.path.join(root, file)
                        analysis["total_files"] += 1

                        # Count lines
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                analysis["total_lines"] += len(lines)
                        except:
                            pass

                        # Language detection
                        ext = os.path.splitext(file)[1]
                        analysis["languages"][ext] = analysis["languages"].get(ext, 0) + 1

                        # Count skills
                        if 'skills/' in root and file.endswith('.py') and not file.startswith('__'):
                            analysis["skills_count"] += 1

            # Generate recommendations
            if analysis["skills_count"] < 10:
                analysis["recommendations"].append("Considerar expandir el conjunto de skills disponibles")

            if analysis["total_lines"] > 10000:
                analysis["recommendations"].append("El codebase está creciendo - considerar modularización adicional")

            if '.py' in analysis["languages"] and analysis["languages"]['.py'] > 20:
                analysis["issues"].append("Múltiples archivos Python - asegurar consistencia de estilo")

            return {
                "success": True,
                "analysis": analysis
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analizando codebase: {str(e)}"
            }

    def _generate_skill(self, skill_name: str, description: str) -> Dict[str, Any]:
        """Generate a basic skill template"""
        if not skill_name or not description:
            return {
                "success": False,
                "error": "Se requiere nombre del skill y descripción"
            }

        # Create skill filename
        filename = f"{skill_name.lower().replace(' ', '_')}.py"
        filepath = os.path.join(self.jarvis_root, 'skills', filename)

        # Check if file already exists
        if os.path.exists(filepath):
            return {
                "success": False,
                "error": f"El skill '{skill_name}' ya existe"
            }

        # Generate skill template
        template = f'''# skills/{filename}
"""
{skill_name} Skill - {description}
Generated automatically by Auto Programming Skill
"""

from typing import Dict, Any


class {skill_name.replace(' ', '').replace('_', '')}Skill:
    """
    {description}
    """

    def __init__(self, **kwargs):
        # Initialize skill with any dependencies
        pass

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the {skill_name} skill.

        Returns:
            Result of the skill execution
        """
        try:
            # TODO: Implement skill logic here
            return {{
                "success": True,
                "message": "{skill_name} skill ejecutado exitosamente",
                "result": "Implementación pendiente"
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": f"Error ejecutando {skill_name}: {{str(e)}}"
            }}
'''

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)

            return {
                "success": True,
                "message": f"Skill '{skill_name}' generado exitosamente",
                "filepath": filepath,
                "next_steps": [
                    "Implementar la lógica en el método run()",
                    "Agregar el skill al registro en engine.py",
                    "Crear tests para el nuevo skill"
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creando skill: {str(e)}"
            }

    def _optimize_codebase(self) -> Dict[str, Any]:
        """Suggest optimizations for the codebase"""
        optimizations = {
            "code_quality": [],
            "performance": [],
            "maintainability": [],
            "security": []
        }

        try:
            # Analyze Python files for common issues
            for root, dirs, files in os.walk(self.jarvis_root):
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Check for common issues
                            if 'print(' in content and 'logger' not in content:
                                optimizations["code_quality"].append(f"Reemplazar prints con logging en {file}")

                            if 'except:' in content and 'Exception' not in content:
                                optimizations["code_quality"].append(f"Captura demasiado amplia en {file}")

                            if len(content.split('\n')) > 500:
                                optimizations["maintainability"].append(f"Archivo largo detectado: {file} - considerar dividir")

                        except:
                            continue

            # Performance suggestions
            optimizations["performance"].append("Considerar cache para operaciones repetitivas")
            optimizations["performance"].append("Optimizar consultas a base de datos con índices")

            # Security suggestions
            optimizations["security"].append("Revisar manejo de inputs del usuario")
            optimizations["security"].append("Implementar rate limiting para APIs")

            return {
                "success": True,
                "optimizations": optimizations,
                "total_suggestions": sum(len(v) for v in optimizations.values())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error analizando optimizaciones: {str(e)}"
            }

    def _diagnose_issues(self) -> Dict[str, Any]:
        """Diagnose potential issues in the system"""
        issues = {
            "critical": [],
            "warnings": [],
            "info": []
        }

        try:
            # Check for missing dependencies
            try:
                import psutil
            except ImportError:
                issues["critical"].append("psutil no instalado - requerido para system monitoring")

            try:
                import requests
            except ImportError:
                issues["warnings"].append("requests no instalado - limita capacidades de red")

            # Check configuration
            config_path = os.path.join(self.jarvis_root, 'config.json')
            if not os.path.exists(config_path):
                issues["critical"].append("config.json no encontrado")

            # Check for empty files
            empty_files = []
            for root, dirs, files in os.walk(self.jarvis_root):
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                if len(f.read().strip()) < 50:  # Very small files
                                    empty_files.append(file)
                        except:
                            continue

            if empty_files:
                issues["info"].append(f"Archivos potencialmente incompletos: {', '.join(empty_files[:5])}")

            # Check for unused imports (basic)
            issues["info"].append("Considerar análisis estático de código para imports no utilizados")

            return {
                "success": True,
                "diagnosis": issues,
                "total_issues": sum(len(v) for v in issues.values())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error en diagnóstico: {str(e)}"
            }

    def _create_configuration(self, config_type: str) -> Dict[str, Any]:
        """Create configuration templates"""
        configs = {
            "llm": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "your-api-key-here",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            "audio": {
                "stt_enabled": True,
                "tts_enabled": True,
                "wake_word": "jarvis",
                "audio_device": "default"
            },
            "monitoring": {
                "enable_metrics": True,
                "log_level": "INFO",
                "alerts_enabled": True,
                "performance_monitoring": True
            }
        }

        if config_type not in configs:
            return {
                "success": False,
                "error": f"Tipo de configuración desconocido: {config_type}",
                "available_types": list(configs.keys())
            }

        config_path = os.path.join(self.jarvis_root, f"{config_type}_config.json")

        try:
            import json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(configs[config_type], f, indent=2)

            return {
                "success": True,
                "message": f"Configuración {config_type} creada en {config_path}",
                "config": configs[config_type]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creando configuración: {str(e)}"
            }