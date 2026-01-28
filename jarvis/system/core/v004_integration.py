"""
Jarvis v0.0.4 Integration Module
Connects all new v0.0.4 components to JarvisCore

This module provides a clean integration layer that:
1. Imports all v0.0.4 components
2. Wires them into JarvisCore
3. Provides hooks for handlers.py to use
4. Enables debug mode with NLU tracing
5. Supports background task execution
6. Integrates PC monitoring
"""

import logging
import sys
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class V004IntegrationLayer:
    """
    Layer that integrates v0.0.4 components into JarvisCore
    """
    
    def __init__(self, jarvis_core):
        """Initialize integration layer with a JarvisCore instance"""
        self.jarvis = jarvis_core
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all v0.0.4 components"""
        try:
            # 1. Import ComprehensionScorer
            try:
                from system.pc_authority.comprehension_scorer import ComprehensionScorer
                self.jarvis.comprehension_scorer = ComprehensionScorer()
                logger.info("✓ ComprehensionScorer initialized")
            except Exception as e:
                logger.warning(f"Could not import ComprehensionScorer: {e}")
                self.jarvis.comprehension_scorer = None
            
            # 2. Import ProcessMonitor
            try:
                from system.pc_authority.process_monitor import ProcessMonitor
                self.jarvis.process_monitor = ProcessMonitor()
                logger.info("✓ ProcessMonitor initialized")
            except Exception as e:
                logger.warning(f"Could not import ProcessMonitor: {e}")
                self.jarvis.process_monitor = None
            
            # 3. Import BackgroundTaskManager
            try:
                from system.pc_authority.background_task_manager import BackgroundTaskManager
                self.jarvis.task_manager = BackgroundTaskManager(max_workers=4)
                logger.info("✓ BackgroundTaskManager initialized")
            except Exception as e:
                logger.warning(f"Could not import BackgroundTaskManager: {e}")
                self.jarvis.task_manager = None
            
            # 4. Import SystemAuthorityController
            try:
                from system.pc_authority.system_authority import SystemAuthorityController
                self.jarvis.system_authority = SystemAuthorityController()
                logger.info("✓ SystemAuthorityController initialized")
            except Exception as e:
                logger.warning(f"Could not import SystemAuthorityController: {e}")
                self.jarvis.system_authority = None
            
            # 5. Import soft phrases
            try:
                from brain.nlu.soft_phrases import SoftPhrasesDatabase
                self.jarvis.soft_phrases = SoftPhrasesDatabase()
                logger.info(f"✓ SoftPhrasesDatabase initialized ({len(self.jarvis.soft_phrases.get_all_phrases())} phrases)")
            except Exception as e:
                logger.warning(f"Could not import SoftPhrasesDatabase: {e}")
                self.jarvis.soft_phrases = None
            
        except Exception as e:
            logger.error(f"Error initializing v0.0.4 components: {e}")
    
    def enhance_nlu_processing(self, user_input: str) -> Dict[str, Any]:
        """
        Enhance NLU processing with ComprehensionScorer and soft phrases
        
        Returns:
            dict with 'intent', 'confidence', 'entities', 'matched_phrase' (if applicable)
        """
        result = {
            'original_input': user_input,
            'matched_soft_phrase': None,
            'scored_comprehension': None,
            'final_intent': None,
            'final_confidence': 0.0,
            'debug_trace': [] if self.jarvis.get_debug_status() else None
        }
        
        try:
            # Step 1: Try soft phrases first
            if self.jarvis.soft_phrases:
                phrase_match = self.jarvis.soft_phrases.match_user_input(user_input)
                if phrase_match and phrase_match['confidence'] > 0.7:
                    result['matched_soft_phrase'] = phrase_match
                    result['final_intent'] = phrase_match['intent']
                    result['final_confidence'] = phrase_match['confidence']
                    
                    if self.jarvis.get_debug_status():
                        result['debug_trace'].append(f"✓ Soft phrase matched: {phrase_match['intent']} ({phrase_match['confidence']:.2f})")
                    
                    return result
            
            # Step 2: Use standard NLU pipeline
            if hasattr(self.jarvis, 'nlu'):
                nlu_result = self.jarvis.nlu.process(user_input)
                
                if self.jarvis.get_debug_status():
                    result['debug_trace'].append(f"NLU raw result: {nlu_result['intent']} ({nlu_result['confidence']:.2f})")
                
                # Step 3: Score comprehension
                if self.jarvis.comprehension_scorer:
                    scored = self.jarvis.comprehension_scorer.score_comprehension(
                        user_input=user_input,
                        detected_intent=nlu_result['intent'],
                        detected_confidence=nlu_result['confidence'],
                        entities=nlu_result.get('entities', {})
                    )
                    
                    result['scored_comprehension'] = scored
                    result['final_intent'] = scored['refined_intent']
                    result['final_confidence'] = scored['final_confidence']
                    
                    if self.jarvis.get_debug_status():
                        result['debug_trace'].append(
                            f"Comprehension scored: {scored['refined_intent']} "
                            f"({scored['final_confidence']:.2f}) - "
                            f"Confidence level: {scored['confidence_level']}"
                        )
                else:
                    result['final_intent'] = nlu_result['intent']
                    result['final_confidence'] = nlu_result['confidence']
            
        except Exception as e:
            logger.error(f"Error in enhanced NLU processing: {e}")
            if self.jarvis.get_debug_status():
                result['debug_trace'].append(f"ERROR: {str(e)}")
        
        return result
    
    def execute_with_background_task(self, task_name: str, function: Callable, 
                                    args=None, kwargs=None, priority: int = 0,
                                    wait_for_response: bool = False) -> Dict[str, Any]:
        """
        Execute a skill function, potentially in background
        
        Args:
            task_name: Name of the task
            function: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority (0-9, higher = more important)
            wait_for_response: If True, wait for completion; if False, return immediately
        
        Returns:
            dict with task_id, status, result (if completed)
        """
        try:
            args = args or ()
            kwargs = kwargs or {}
            
            if wait_for_response or not self.jarvis.task_manager:
                # Execute synchronously
                result = function(*args, **kwargs)
                return {
                    'task_id': None,
                    'status': 'COMPLETED',
                    'result': result,
                    'async': False
                }
            else:
                # Execute asynchronously
                task_id = self.jarvis.task_manager.submit_task(
                    task_id=f"bg_task_{hash(task_name) % 10000}",
                    name=task_name,
                    function=function,
                    args=args,
                    kwargs=kwargs,
                    priority=priority
                )
                
                return {
                    'task_id': task_id,
                    'status': 'SUBMITTED',
                    'result': None,
                    'async': True,
                    'message': f"Task '{task_name}' submitted to background. ID: {task_id}"
                }
        
        except Exception as e:
            logger.error(f"Error executing background task: {e}")
            return {
                'error': str(e),
                'status': 'FAILED'
            }
    
    def get_natural_response(self, intent: str, entities: Dict = None, 
                           skill_result: Dict = None) -> str:
        """
        Get natural language response using soft phrases and skill results
        
        Args:
            intent: The matched intent
            entities: Extracted entities
            skill_result: Result from skill execution
        
        Returns:
            Natural language response string
        """
        try:
            entities = entities or {}
            skill_result = skill_result or {}
            
            # Try to get response from soft phrases
            if self.jarvis.soft_phrases:
                response = self.jarvis.soft_phrases.get_response(intent, entities)
                if response:
                    return response
            
            # Fallback to generic response
            if 'response' in skill_result:
                return skill_result['response']
            
            return f"Completado: {intent}"
        
        except Exception as e:
            logger.error(f"Error getting natural response: {e}")
            return f"Error procesando respuesta para {intent}"


# Create global integration instance (lazy loaded)
_integration_instance = None


def get_integration_layer(jarvis_core) -> V004IntegrationLayer:
    """Get or create the integration layer"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = V004IntegrationLayer(jarvis_core)
    return _integration_instance


def integrate_v004_into_engine(jarvis_core):
    """
    Main function to integrate v0.0.4 into an existing JarvisCore instance
    
    Should be called after JarvisCore initialization but before processing user input
    """
    try:
        integration = V004IntegrationLayer(jarvis_core)
        
        # Add the integration layer to jarvis_core
        jarvis_core.integration_layer = integration
        
        logger.info("✓ v0.0.4 integration layer initialized")
        return integration
    
    except Exception as e:
        logger.error(f"Failed to integrate v0.0.4: {e}")
        return None


__all__ = ['V004IntegrationLayer', 'get_integration_layer', 'integrate_v004_into_engine']
