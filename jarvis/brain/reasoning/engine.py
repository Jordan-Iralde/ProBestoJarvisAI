"""
Reasoning Engine v0.0.4
Minimal but robust reasoning system for intent validation and skill planning.
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime


class ReasoningResult:
    """Encapsulates reasoning output"""
    
    def __init__(self, intent: str, entities: Dict[str, Any]):
        self.intent = intent
        self.entities = entities
        self.valid = True
        self.confidence = 1.0
        self.warnings: List[str] = []
        self.reasons: List[str] = []  # Why this decision
        self.alternatives: List[Tuple[str, float]] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_warning(self, warning: str):
        """Add reasoning warning"""
        self.warnings.append(warning)
    
    def add_reason(self, reason: str):
        """Add reasoning explanation"""
        self.reasons.append(reason)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging"""
        return {
            "intent": self.intent,
            "entities": self.entities,
            "valid": self.valid,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "reasons": self.reasons,
            "alternatives": self.alternatives,
            "metadata": self.metadata
        }


class ReasoningEngine:
    """
    Validates intents and reasons about skill execution
    
    Features:
    - Intent validation (is it safe/valid?)
    - Entity consistency checking
    - Dependency resolution
    - Conflict detection
    - Risk assessment
    """
    
    def __init__(self):
        self.skill_rules: Dict[str, List[callable]] = {}  # Rules per intent
        self.global_rules: List[callable] = []  # Rules for all intents
        self.reasoning_history: List[ReasoningResult] = []
    
    def register_skill_rule(self, intent: str, rule: callable):
        """Register a validation rule for a specific skill"""
        if intent not in self.skill_rules:
            self.skill_rules[intent] = []
        self.skill_rules[intent].append(rule)
    
    def register_global_rule(self, rule: callable):
        """Register a rule that applies to all skills"""
        self.global_rules.append(rule)
    
    def reason(self, intent: str, entities: Dict[str, Any], 
               context: Optional[Dict] = None) -> ReasoningResult:
        """
        Reason about intent execution
        
        Args:
            intent: Intent to reason about
            entities: Extracted entities
            context: Optional execution context
            
        Returns:
            ReasoningResult with validity and reasoning
        """
        result = ReasoningResult(intent, entities)
        context = context or {}
        
        # Step 1: Global validation
        for rule in self.global_rules:
            try:
                rule_valid, rule_reason = rule(intent, entities, context)
                if not rule_valid:
                    result.add_warning(rule_reason)
                    result.add_reason(f"Global rule failed: {rule_reason}")
                else:
                    result.add_reason(f"Global rule passed: {rule_reason}")
            except Exception as e:
                result.add_warning(f"Rule error: {str(e)}")
        
        # Step 2: Skill-specific validation
        if intent in self.skill_rules:
            for rule in self.skill_rules[intent]:
                try:
                    rule_valid, rule_reason = rule(entities, context)
                    if not rule_valid:
                        result.add_warning(rule_reason)
                        result.add_reason(f"Skill rule failed: {rule_reason}")
                        result.valid = False
                    else:
                        result.add_reason(f"Skill rule passed: {rule_reason}")
                except Exception as e:
                    result.add_warning(f"Skill rule error: {str(e)}")
        
        # Step 3: Entity validation
        result.add_reason(f"Entities present: {list(entities.keys())}")
        
        # Store in history
        self.reasoning_history.append(result)
        if len(self.reasoning_history) > 100:
            self.reasoning_history = self.reasoning_history[-100:]
        
        return result
    
    def get_reasoning_stats(self) -> Dict[str, Any]:
        """Get reasoning statistics"""
        if not self.reasoning_history:
            return {"total": 0}
        
        valid_count = sum(1 for r in self.reasoning_history if r.valid)
        
        return {
            "total_reasonings": len(self.reasoning_history),
            "valid": valid_count,
            "invalid": len(self.reasoning_history) - valid_count,
            "validity_rate": f"{(valid_count / len(self.reasoning_history)) * 100:.1f}%"
        }


class SimpleReasoningRules:
    """Built-in reasoning rules"""
    
    @staticmethod
    def require_entity(entity_name: str, error_msg: str = None):
        """Create rule that requires an entity"""
        def rule(entities: Dict, context: Dict):
            if entity_name in entities:
                return True, f"Entity '{entity_name}' present"
            return False, error_msg or f"Missing required entity: {entity_name}"
        return rule
    
    @staticmethod
    def require_context_key(key: str, error_msg: str = None):
        """Create rule that requires a context key"""
        def rule(entities: Dict, context: Dict):
            if key in context:
                return True, f"Context key '{key}' available"
            return False, error_msg or f"Missing context: {key}"
        return rule
    
    @staticmethod
    def check_entity_type(entity_name: str, expected_type: type):
        """Create rule that checks entity type"""
        def rule(entities: Dict, context: Dict):
            if entity_name not in entities:
                return True, f"Entity '{entity_name}' not present (optional)"
            
            value = entities[entity_name]
            if isinstance(value, expected_type):
                return True, f"Entity '{entity_name}' has correct type"
            return False, f"Entity '{entity_name}' has wrong type: expected {expected_type.__name__}, got {type(value).__name__}"
        return rule
    
    @staticmethod
    def check_mode_permission(allowed_modes: List[str]):
        """Create rule that checks mode permissions"""
        def rule(intent: str, entities: Dict, context: Dict):
            current_mode = context.get("mode", "PASSIVE")
            if current_mode in allowed_modes:
                return True, f"Mode '{current_mode}' allowed for {intent}"
            return False, f"Mode '{current_mode}' not allowed for {intent}. Allowed: {allowed_modes}"
        return rule
