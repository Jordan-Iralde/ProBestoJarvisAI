# system/core/parallel_executor.py
"""
Parallel Executor v0.0.4
Attempts multiple skills in parallel when intent confidence is low
"""

from typing import Dict, List, Optional, Any
import time
import threading


class ParallelExecutor:
    """
    Execute multiple skill alternatives in parallel
    Used when intent confidence is low (< 0.7)
    Returns first successful result or most promising failure
    """
    
    def __init__(self, dispatcher, logger=None, timeout_seconds=5.0):
        """
        Args:
            dispatcher: SkillDispatcher instance
            logger: logging.Logger instance
            timeout_seconds: Max time to wait for parallel attempts
        """
        self.dispatcher = dispatcher
        self.logger = logger
        self.timeout = timeout_seconds
    
    def _log(self, msg: str):
        """Log message"""
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[PARALLEL] {msg}")
    
    def attempt_alternatives(self, primary_intent: str, alternatives: List[tuple],
                            entities: Dict[str, Any], core) -> Dict[str, Any]:
        """
        Attempt primary intent and alternatives in parallel
        
        Args:
            primary_intent: Main recognized intent
            alternatives: List of (intent_name, confidence) tuples
            entities: Extracted entities
            core: JarvisCore instance
        
        Returns:
            Dict with best result from any attempt
        """
        # Build list of intents to try
        intents_to_try = [(primary_intent, 1.0)]  # Primary first
        intents_to_try.extend(alternatives[:2])  # Top 2 alternatives
        
        results = {}
        threads = []
        results_lock = threading.Lock()
        
        def attempt_skill(intent_name: str, confidence: float):
            """Try executing a single skill"""
            try:
                self._log(f"Attempting: {intent_name} ({confidence:.2%})")
                start = time.time()
                
                result = self.dispatcher.dispatch(intent_name, entities, core)
                duration = time.time() - start
                
                with results_lock:
                    results[intent_name] = {
                        'intent': intent_name,
                        'confidence': confidence,
                        'result': result,
                        'duration_ms': int(duration * 1000),
                        'success': result.get('success', False) if isinstance(result, dict) else True
                    }
                
                if results[intent_name]['success']:
                    self._log(f"✅ Success: {intent_name}")
                else:
                    self._log(f"❌ Failed: {intent_name}")
            
            except Exception as e:
                with results_lock:
                    results[intent_name] = {
                        'intent': intent_name,
                        'confidence': confidence,
                        'error': str(e),
                        'success': False
                    }
                self._log(f"❌ Error in {intent_name}: {str(e)[:50]}")
        
        # Start all attempts in parallel
        for intent, conf in intents_to_try:
            thread = threading.Thread(
                target=attempt_skill,
                args=(intent, conf),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all attempts (with timeout)
        for thread in threads:
            thread.join(timeout=self.timeout / len(threads))
        
        # Find best result: prefer success, then confidence, then duration
        if not results:
            return {
                'success': False,
                'error': 'No results from parallel execution',
                'attempted_intents': len(intents_to_try)
            }
        
        # Find successful result
        successful = [r for r in results.values() if r.get('success')]
        if successful:
            # Return highest confidence successful result
            best = max(successful, key=lambda x: x.get('confidence', 0))
            self._log(f"🎯 Using result from: {best['intent']}")
            return best
        
        # All failed - return primary with alternatives info
        primary_result = results.get(primary_intent, {})
        primary_result['alternatives_attempted'] = [
            {
                'intent': r['intent'],
                'confidence': r['confidence'],
                'success': r.get('success', False)
            }
            for r in results.values()
            if r['intent'] != primary_intent
        ]
        
        self._log(f"⚠️ All attempts failed, returning primary: {primary_intent}")
        return primary_result
    
    def get_best_result(self, results: Dict) -> Dict[str, Any]:
        """Get best result from parallel execution results"""
        if not results:
            return {'success': False, 'error': 'No results'}
        
        # Prefer successful results
        successful = [r for r in results.values() if r.get('success')]
        if successful:
            return max(successful, key=lambda x: (x.get('confidence', 0), 1.0 / (x.get('duration_ms', 1) + 1)))
        
        # All failed - return least error-prone
        return min(results.values(), key=lambda x: x.get('duration_ms', 9999))
