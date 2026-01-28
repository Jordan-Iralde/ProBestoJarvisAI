# system/core/intent_validator.py
"""
Intent Validator - Ask user to confirm if Jarvis understood correctly
Especially useful for low-confidence intents
"""

from typing import Optional, Tuple


class IntentValidator:
    """
    Validates intent by asking user for feedback when confidence is low
    Or after execution completes
    """
    
    def __init__(self, cli, reflection_observer):
        self.cli = cli
        self.reflection = reflection_observer
        self.feedback_enabled = True
    
    def should_ask_feedback(self, confidence: float, intent: str) -> bool:
        """
        Decide if we should ask user for feedback
        - Low confidence (<0.65) → Always ask
        - Medium confidence (0.65-0.8) → Ask after execution
        - High confidence (>0.8) → Don't ask
        """
        return confidence < 0.8 and intent != 'unknown'
    
    def ask_before_execution(self, intent: str, confidence: float, 
                            alternatives: list, input_text: str) -> Tuple[bool, Optional[str]]:
        """
        Ask user if they want to proceed with this intent
        Returns: (proceed: bool, corrected_intent: Optional[str])
        """
        if not self.feedback_enabled or confidence >= 0.8:
            return True, None
        
        conf_pct = int(confidence * 100)
        
        print()
        self.cli.print_thought(f"Entendí '{intent}' con {conf_pct}% de confianza")
        
        if alternatives:
            print("  Otras opciones:")
            options = ['✓ Continuar con ' + intent]
            for i, (alt_intent, alt_conf) in enumerate(alternatives[:2]):
                alt_pct = int(alt_conf * 100)
                options.append(f"{chr(97+i)}) Intentar con '{alt_intent}' ({alt_pct}%)")
            options.append("n) Cancelar")
            
            for opt in options:
                print(f"  {opt}")
            
            # In interactive mode, we would get user input here
            # For now, return proceed=True to continue
            return True, None
        
        return True, None
    
    def ask_after_execution(self, intent: str, success: bool, 
                           result: any, execution_time_ms: int) -> bool:
        """
        Ask user if the result was what they wanted
        Returns: was_correct (bool)
        """
        if not self.feedback_enabled:
            return success
        
        # Only ask for failed or low-confidence operations
        if success:
            return True
        
        print()
        print("  ¿Fue correcta la interpretación?")
        print("    y) Sí, gracias")
        print("    n) No, quería otra cosa")
        
        # In interactive mode, we would get user input
        # For now, return success
        return success
    
    def validate_alternatives(self, input_text: str, intent: str, 
                             alternatives: list, confidence: float) -> Optional[str]:
        """
        Compare primary intent vs alternatives
        Returns: best_intent (str)
        """
        # Check if we have reflection data about similar inputs
        pattern = self.reflection.get_decision_pattern(input_text) if self.reflection else None
        
        if pattern and pattern['user_confirmed']:
            # We learned this pattern before
            return pattern['intent']
        
        # Return primary intent
        return intent
