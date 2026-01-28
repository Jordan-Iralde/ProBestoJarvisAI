# brain/nlu/pipeline.py
"""
NLU Pipeline v0.0.4 - Enhanced with confidence scores, tracing, error handling, and context awareness
"""
import traceback
from typing import Dict, List, Optional, Tuple
from brain.nlu.normalizer import Normalizer
from brain.nlu.entities import EntityExtractor
from brain.nlu.parser import IntentParser
from system.core.exceptions import NLUError
from brain.memory.context import ContextManager


class NLUResult:
    """Encapsulates NLU processing result with metadata"""
    
    def __init__(self, intent: str, entities: Dict, raw_text: str, normalized_text: str):
        self.intent = intent
        self.entities = entities
        self.raw_text = raw_text
        self.normalized_text = normalized_text
        self.confidence = 0.0
        self.alternatives = []  # List of (intent, confidence) tuples
        self.trace = []  # Debug trace steps
        self.error = None
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for event emission"""
        return {
            "intent": self.intent,
            "entities": self.entities,
            "raw": self.raw_text,
            "normalized": self.normalized_text,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "trace": self.trace if self.trace else None
        }


class NLUPipeline:
    """
    NLU Pipeline with confidence scoring, debug tracing, and context awareness
    """
    
    def __init__(self, skills_registry, debug=False, context_manager=None):
        self.norm = Normalizer()
        self.entities = EntityExtractor(skills_registry)
        self.intent = IntentParser(skills_registry)
        self.debug = debug
        self.skills_registry = skills_registry
        self.confidence_threshold = 0.5  # Minimum confidence for intent recognition
        self.context = context_manager or ContextManager()  # Always use context

    def _log(self, *msg):
        """Log debug messages if debug mode enabled"""
        if self.debug:
            print("[NLU]", *msg)
    
    def _trace(self, result: NLUResult, step: str, details: str):
        """Add trace step for debugging"""
        trace_entry = {
            "step": step,
            "details": details
        }
        result.trace.append(trace_entry)
        self._log(f"TRACE[{step}]: {details}")

    def process(self, text: str, eventbus) -> Optional[NLUResult]:
        """
        Process text through NLU pipeline with confidence scoring and context awareness
        
        Args:
            text: Input text to process
            eventbus: Event bus for emitting results
            
        Returns:
            NLUResult object with intent, entities, and confidence
        """
        result = NLUResult(
            intent="unknown",
            entities={},
            raw_text=text.strip(),
            normalized_text=""
        )
        
        try:
            raw = text.strip()
            if not raw:
                result.error = "Empty input"
                self._trace(result, "validation", "Input is empty")
                return result

            # Step 1: Normalization
            try:
                clean = self.norm.run(raw)
                result.normalized_text = clean
                self._trace(result, "normalize", f"'{raw}' → '{clean}'")
            except Exception as e:
                result.error = f"Normalization failed: {str(e)}"
                self._trace(result, "normalize", f"ERROR: {str(e)}")
                raise NLUError(result.error, {"input": raw})

            # Step 2: Entity Extraction
            try:
                ent = self.entities.extract(clean)
                result.entities = ent
                self._trace(result, "entities", f"Found {len(ent)} entities: {list(ent.keys())}")
                
                eventbus.emit("nlu.entities.detected", {
                    "raw": raw,
                    "normalized": clean,
                    "entities": ent
                })
            except Exception as e:
                result.error = f"Entity extraction failed: {str(e)}"
                self._trace(result, "entities", f"ERROR: {str(e)}")
                # Don't raise - continue without entities
                ent = {}

            # Step 3: Intent Parsing with Confidence
            try:
                intent_name, confidence = self.intent.parse_with_confidence(clean, ent)
                result.intent = intent_name
                result.confidence = confidence
                
                self._trace(result, "intent", f"Intent='{intent_name}' confidence={confidence:.2f}")
                
                # Get alternative intents if confidence is low
                if confidence < 0.8:
                    alternatives = self.intent.get_alternatives(clean, ent, top_n=2)
                    result.alternatives = alternatives
                    self._trace(result, "alternatives", f"Alternatives: {alternatives}")
                
            except Exception as e:
                result.error = f"Intent parsing failed: {str(e)}"
                result.intent = "unknown"
                result.confidence = 0.0
                self._trace(result, "intent", f"ERROR: {str(e)}")
                raise NLUError(result.error, {"normalized": clean, "entities": ent})

            # Step 4: Store in context for future reference
            try:
                self.context.add_intent(result.intent, result.confidence, result.entities)
                self._trace(result, "context", f"Stored in context manager")
            except Exception as e:
                # Log but don't fail on context storage
                self._trace(result, "context", f"WARNING: {str(e)}")
            
            # Emit NLU intent event
            eventbus.emit("nlu.intent", result.to_dict())
            
            return result

        except NLUError:
            # Re-raise NLU errors
            eventbus.emit("nlu.error", {
                "error": result.error,
                "text": text,
                "trace": result.trace
            })
            raise
        except Exception as e:
            # Catch unexpected errors
            result.error = f"Unexpected NLU error: {str(e)}"
            self._trace(result, "exception", f"Unexpected: {str(e)}")
            
            print(f"[NLU_ERROR] Unexpected error: {e}")
            traceback.print_exc()
            
            eventbus.emit("nlu.error", {
                "error": result.error,
                "text": text,
                "trace": result.trace,
                "traceback": traceback.format_exc()
            })
            raise NLUError(result.error, {"input": text})
