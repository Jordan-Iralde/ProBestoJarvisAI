# system/logging/manager.py
import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class JarvisLogger:
    """
    Sistema de logging profesional con persistencia.
    Guarda logs en Desktop para transparencia total.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Carpeta en Desktop para transparencia
        desktop = Path.home() / "Desktop" / "JarvisData"
        desktop.mkdir(exist_ok=True)
        
        self.logs_dir = desktop / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        self._setup_logging()
        
        # Métricas en memoria
        self.metrics = {
            "commands_processed": 0,
            "skills_executed": {},
            "errors": [],
            "session_start": datetime.now().isoformat()
        }
        
        self.logger.info("JarvisLogger initialized")
        self.logger.info(f"Logs guardados en: {self.logs_dir}")
    
    def _setup_logging(self):
        """Configura el sistema de logging con múltiples handlers"""
        
        # Logger principal
        self.logger = logging.getLogger("Jarvis")
        self.logger.setLevel(logging.DEBUG if self.config.get("debug") else logging.INFO)
        
        # Formato detallado
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler 1: Archivo general
        log_file = self.logs_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler 2: Archivo de errores
        error_file = self.logs_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler 3: Console (solo INFO+)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s | %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log_command(self, command: str, intent: str, entities: Dict, success: bool):
        """Log de comandos ejecutados"""
        self.metrics["commands_processed"] += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "intent": intent,
            "entities": entities,
            "success": success
        }
        
        self.logger.info(f"Command: {command} → {intent} (success: {success})")
        
        # Guardar en archivo JSON para análisis
        commands_file = self.logs_dir / "commands_history.jsonl"
        with open(commands_file, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def log_skill_execution(self, skill_name: str, result: Dict, duration: float):
        """Log de ejecución de skills"""
        if skill_name not in self.metrics["skills_executed"]:
            self.metrics["skills_executed"][skill_name] = 0
        self.metrics["skills_executed"][skill_name] += 1
        
        self.logger.info(f"Skill executed: {skill_name} ({duration:.3f}s)")
        
        # Guardar detalles
        skills_file = self.logs_dir / "skills_execution.jsonl"
        with open(skills_file, "a", encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "skill": skill_name,
                "duration_ms": duration * 1000,
                "result": result
            }, ensure_ascii=False) + "\n")
    
    def log_error(self, error_type: str, error_msg: str, context: Dict = None):
        """Log de errores"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_msg,
            "context": context or {}
        }
        
        self.metrics["errors"].append(error_entry)
        self.logger.error(f"{error_type}: {error_msg}")
        
        # Mantener solo últimos 100 errores
        if len(self.metrics["errors"]) > 100:
            self.metrics["errors"].pop(0)
    
    def get_metrics(self) -> Dict:
        """Retorna métricas actuales"""
        return {
            **self.metrics,
            "session_duration": (
                datetime.now() - 
                datetime.fromisoformat(self.metrics["session_start"])
            ).total_seconds()
        }
    
    def save_metrics(self):
        """Guarda métricas a disco"""
        metrics_file = self.logs_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, "w", encoding='utf-8') as f:
            json.dump(self.get_metrics(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metrics saved to {metrics_file}")
