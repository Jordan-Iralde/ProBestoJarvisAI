# brain/reflection_observer.py
"""
Post-Skill Reflection Observer v0.0.4
Records what happened after skill execution and learns from feedback
"""

from typing import Dict, List, Optional
from datetime import datetime


class SkillReflectionRecord:
    """Single reflection record after skill execution"""
    
    def __init__(self, intent: str, skill_name: str, input_text: str, 
                 confidence: float, alternatives: list):
        self.timestamp = datetime.now().isoformat()
        self.intent = intent
        self.skill_name = skill_name
        self.input_text = input_text
        self.confidence = confidence
        self.alternatives = alternatives or []
        
        # Execution results
        self.success = None
        self.result = None
        self.error = None
        self.duration_ms = 0
        
        # Feedback
        self.user_feedback = None  # "correct", "wrong", "alternative"
        self.alternative_intent = None
        self.user_notes = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'timestamp': self.timestamp,
            'intent': self.intent,
            'skill_name': self.skill_name,
            'input_text': self.input_text,
            'confidence': self.confidence,
            'alternatives': self.alternatives,
            'success': self.success,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'user_feedback': self.user_feedback,
            'alternative_intent': self.alternative_intent,
            'user_notes': self.user_notes
        }


class SkillReflectionObserver:
    """
    Observes skill execution and learns from outcomes + user feedback
    
    Flow:
    1. Skill executes → record what happened
    2. User provides feedback (correct/wrong/alternative)
    3. Store decision for future learning
    4. Suggest alternatives if confidence was low
    """
    
    def __init__(self, storage=None, logger=None):
        self.storage = storage
        self.logger = logger
        self.current_reflection = None
        self.reflection_history = []
    
    def _log(self, msg: str):
        """Log message using logger or print"""
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[REFLECTION] {msg}")
    
    def start_recording(self, intent: str, skill_name: str, input_text: str,
                       confidence: float, alternatives: list = None) -> SkillReflectionRecord:
        """
        Start recording a skill execution
        Called BEFORE skill runs
        """
        record = SkillReflectionRecord(
            intent=intent,
            skill_name=skill_name,
            input_text=input_text,
            confidence=confidence,
            alternatives=alternatives or []
        )
        self.current_reflection = record
        self._log(f"Recording: {intent} (confidence={confidence:.2%})")
        return record
    
    def record_execution(self, success: bool, result: any = None, 
                        error: str = None, duration_ms: int = 0):
        """
        Record skill execution outcome
        Called AFTER skill runs
        """
        if not self.current_reflection:
            self._log("No active reflection record")
            return
        
        self.current_reflection.success = success
        self.current_reflection.result = result
        self.current_reflection.error = error
        self.current_reflection.duration_ms = duration_ms
        
        status = "SUCCESS" if success else "FAILED"
        self._log(f"{status}: {self.current_reflection.intent} in {duration_ms}ms")
    
    def request_feedback(self, alternatives: List[tuple] = None) -> Dict:
        """
        Request user feedback on the decision made
        Returns options user can choose from
        
        Returns:
        {
            'was_correct': bool,  # Did Jarvis understand correctly?
            'alternative_intent': str,  # If wrong, which is correct?
            'notes': str  # Any additional feedback
        }
        """
        if not self.current_reflection:
            return None
        
        # Build feedback options
        options = [
            f"✓ Correct (understood '{self.current_reflection.intent}')",
        ]
        
        # Add alternatives if available
        if self.current_reflection.alternatives:
            for i, (alt_intent, alt_conf) in enumerate(self.current_reflection.alternatives[:2]):
                options.append(f"{chr(98+i)}) Try '{alt_intent}' instead ({alt_conf:.0%})")
        
        options.append("x) Something else")
        
        return {
            'was_correct': self.current_reflection.success,
            'options': options,
            'input': self.current_reflection.input_text,
            'intent': self.current_reflection.intent
        }
    
    def apply_feedback(self, feedback_type: str, alternative: str = None, notes: str = None):
        """
        Apply user feedback to reflection
        feedback_type: 'correct', 'wrong', 'alternative'
        """
        if not self.current_reflection:
            return
        
        self.current_reflection.user_feedback = feedback_type
        self.current_reflection.alternative_intent = alternative
        self.current_reflection.user_notes = notes
        
        # Store in history
        self.reflection_history.append(self.current_reflection)
        
        # Persist to storage if available
        if self.storage:
            try:
                self.storage.append("reflections", self.current_reflection.to_dict())
                self._log(f"Reflection saved: {feedback_type}")
            except Exception as e:
                self._log(f"Failed to save reflection: {e}")
        
        self.current_reflection = None
    
    def get_decision_pattern(self, input_text: str) -> Optional[Dict]:
        """
        Check if we've seen similar input before and what was the correct intent
        Returns: {'intent': str, 'confidence': float, 'user_confirmed': bool}
        """
        # Search recent reflections for similar input
        for record in self.reflection_history[-50:]:  # Last 50 records
            if record.user_feedback == 'correct' and record.input_text.lower() in input_text.lower():
                return {
                    'intent': record.intent,
                    'confidence': record.confidence,
                    'user_confirmed': True,
                    'timestamp': record.timestamp
                }
        
        return None
    
    def get_problematic_intents(self) -> List[Dict]:
        """
        Find intents that users frequently correct
        Helps identify NLU issues
        """
        wrong_counts = {}
        
        for record in self.reflection_history:
            if record.user_feedback in ['wrong', 'alternative']:
                key = record.intent
                if key not in wrong_counts:
                    wrong_counts[key] = {'count': 0, 'examples': []}
                wrong_counts[key]['count'] += 1
                wrong_counts[key]['examples'].append({
                    'input': record.input_text,
                    'should_be': record.alternative_intent,
                    'timestamp': record.timestamp
                })
        
        # Return sorted by frequency
        return sorted(
            [{'intent': k, **v} for k, v in wrong_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )
    
    def get_insights(self) -> Dict:
        """
        Get learning insights from reflection history
        """
        if not self.reflection_history:
            return {'message': 'No reflection data yet'}
        
        total = len(self.reflection_history)
        correct = sum(1 for r in self.reflection_history if r.user_feedback == 'correct')
        wrong = sum(1 for r in self.reflection_history if r.user_feedback == 'wrong')
        
        accuracy = (correct / total * 100) if total > 0 else 0
        problematic = self.get_problematic_intents()
        
        return {
            'total_decisions': total,
            'correct': correct,
            'wrong': wrong,
            'accuracy_percent': accuracy,
            'top_problematic_intents': problematic[:3],
            'confidence_avg': sum(r.confidence for r in self.reflection_history) / total if total > 0 else 0
        }
