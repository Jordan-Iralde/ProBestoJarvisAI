# brain/memory/adaptive_learning.py
"""
Adaptive Learning Engine - User trains Jarvis's memory
Learns from corrections, user feedback, and successful executions
"""

import json
import time
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


class AdaptiveMemory:
    """
    Adaptive memory system that learns from:
    - User corrections ("No, I meant X")
    - Successful skill executions
    - Failed attempts
    - User preferences
    """
    
    def __init__(self, storage=None):
        self.storage = storage
        self.corrections = {}  # Map incorrect input → correct interpretation
        self.preferences = {}  # User preferences for actions
        self.skill_feedback = {}  # Skill performance feedback
        self.intent_mappings = {}  # Custom intent mappings
        self.app_paths = {}  # Learned app paths
        self.success_patterns = {}  # Successful patterns
    
    def record_correction(self, original_text: str, correct_intent: str, entities: Dict) -> None:
        """User corrects Jarvis"""
        key = original_text.lower().strip()
        
        if key not in self.corrections:
            self.corrections[key] = []
        
        self.corrections[key].append({
            "intent": correct_intent,
            "entities": entities,
            "timestamp": time.time(),
            "weight": 1.0
        })
        
        # Update weight on repeated corrections
        if len(self.corrections[key]) > 1:
            self.corrections[key][-1]["weight"] = len(self.corrections[key]) * 1.5
    
    def record_success(self, text: str, intent: str, entities: Dict, result: Dict) -> None:
        """Record successful skill execution for learning"""
        key = f"{intent}:{str(sorted(entities.items()))}"
        
        if key not in self.success_patterns:
            self.success_patterns[key] = {
                "text_variations": [],
                "success_count": 0,
                "failure_count": 0,
                "avg_confidence": 0.0
            }
        
        pattern = self.success_patterns[key]
        pattern["text_variations"].append(text)
        pattern["success_count"] += 1
        pattern["avg_confidence"] = (pattern["avg_confidence"] + result.get("confidence", 0.8)) / 2
    
    def record_failure(self, text: str, intent: str, error: str) -> None:
        """Record failed execution for learning"""
        key = f"{intent}:{text[:50]}"
        
        if key not in self.skill_feedback:
            self.skill_feedback[key] = {"failures": 0, "errors": []}
        
        self.skill_feedback[key]["failures"] += 1
        self.skill_feedback[key]["errors"].append({
            "error": error,
            "timestamp": time.time()
        })
    
    def record_app_path(self, app_name: str, path: str, confidence: float = 1.0) -> None:
        """Learn where apps are installed"""
        if app_name not in self.app_paths:
            self.app_paths[app_name] = []
        
        self.app_paths[app_name].append({
            "path": path,
            "confidence": confidence,
            "timestamp": time.time(),
            "used_count": 0
        })
    
    def get_correction_for(self, text: str) -> Tuple[str, Dict, float]:
        """Get learned correction for a text"""
        key = text.lower().strip()
        
        if key in self.corrections:
            corrections = self.corrections[key]
            # Sort by weight (most confident)
            best = max(corrections, key=lambda x: x["weight"])
            weight = best["weight"]
            
            # Normalize to 0-1 range
            confidence = min(1.0, weight / 10.0)
            
            return best["intent"], best["entities"], confidence
        
        return None, {}, 0.0
    
    def get_app_path(self, app_name: str) -> str:
        """Get learned path for an app"""
        if app_name in self.app_paths:
            paths = self.app_paths[app_name]
            # Return most successful path
            best = max(paths, key=lambda x: (x["used_count"], x["confidence"]))
            best["used_count"] += 1
            return best["path"]
        
        return None
    
    def get_skill_health(self, skill_name: str) -> Dict:
        """Get health status of a skill"""
        prefix = f"{skill_name}:"
        feedback = {k: v for k, v in self.skill_feedback.items() if k.startswith(prefix)}
        
        total_failures = sum(f.get("failures", 0) for f in feedback.values())
        
        return {
            "skill": skill_name,
            "total_failures": total_failures,
            "is_healthy": total_failures < 3,
            "recent_errors": [
                f["errors"][-1] if f.get("errors") else None
                for f in feedback.values()
            ][:5]
        }
    
    def suggest_improvement(self, skill_name: str) -> str:
        """Suggest how to improve a skill based on failures"""
        health = self.get_skill_health(skill_name)
        
        if health["total_failures"] > 5:
            return f"Skill {skill_name} has {health['total_failures']} failures. Consider debugging or disabling."
        elif health["total_failures"] > 2:
            errors = health["recent_errors"]
            return f"Skill {skill_name} failing recently: {errors[0] if errors else 'Unknown error'}"
        
        return f"Skill {skill_name} is healthy"
    
    def export_learning(self) -> Dict:
        """Export learned data for backup/transfer"""
        return {
            "corrections": self.corrections,
            "app_paths": self.app_paths,
            "success_patterns": self.success_patterns,
            "skill_feedback": self.skill_feedback,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_learning(self, data: Dict) -> None:
        """Import learned data"""
        if "corrections" in data:
            self.corrections.update(data["corrections"])
        if "app_paths" in data:
            self.app_paths.update(data["app_paths"])
        if "success_patterns" in data:
            self.success_patterns.update(data["success_patterns"])
        if "skill_feedback" in data:
            self.skill_feedback.update(data["skill_feedback"])
    
    def get_stats(self) -> Dict:
        """Get learning statistics"""
        total_corrections = sum(len(v) for v in self.corrections.values())
        total_successes = sum(p.get("success_count", 0) for p in self.success_patterns.values())
        total_failures = sum(f.get("failures", 0) for f in self.skill_feedback.values())
        
        return {
            "corrections_learned": total_corrections,
            "successful_patterns": len(self.success_patterns),
            "total_successes": total_successes,
            "total_failures": total_failures,
            "app_paths_learned": len(self.app_paths),
            "success_rate": total_successes / max(1, total_successes + total_failures)
        }
