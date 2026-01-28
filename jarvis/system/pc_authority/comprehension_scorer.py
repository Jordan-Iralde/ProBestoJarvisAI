"""
NLP Enhancement - Comprehension Scoring
Analyzes user intent, provides comprehension score, searches internet if needed
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ComprehensionLevel(Enum):
    """Comprehension confidence levels"""
    VERY_HIGH = (0.95, 1.0, "Muy claro")      # 95-100%
    HIGH = (0.80, 0.95, "Claro")               # 80-95%
    MEDIUM = (0.60, 0.80, "Moderado")          # 60-80%
    LOW = (0.40, 0.60, "Bajo")                 # 40-60%
    VERY_LOW = (0.0, 0.40, "Muy bajo")         # 0-40%


@dataclass
class ComprehensionResult:
    """Result of NLP comprehension analysis"""
    intent: str
    confidence: float
    comprehension_level: str
    comprehension_score: float  # 0.0-1.0
    entities: Dict[str, List[str]]
    user_message: str
    needs_internet_search: bool
    search_terms: List[str]
    alternative_intents: List[Tuple[str, float]]
    clarification_needed: bool
    clarification_question: Optional[str] = None
    reasoning: str = ""


class ComprehensionScorer:
    """Score and analyze NLP comprehension"""

    def __init__(self):
        self.confidence_thresholds = {
            'very_high': 0.95,
            'high': 0.80,
            'medium': 0.60,
            'low': 0.40
        }
        self.internet_keywords = {
            'buscar', 'search', 'find', 'busca', 'encontrar', 'web', 'google',
            'información', 'info', 'dato', 'definición', 'que es', 'como',
            'tutorial', 'guide', 'ayuda', 'help', 'explicación'
        }

    def score_comprehension(self, user_message: str, intent: str, confidence: float,
                           entities: Dict[str, List[str]], 
                           alternative_intents: List[Tuple[str, float]] = None,
                           parser_raw_confidence: float = None) -> ComprehensionResult:
        """
        Score the comprehension of NLP analysis
        
        Args:
            user_message: Original user input
            intent: Detected intent
            confidence: Intent confidence from parser (0.0-1.0)
            entities: Detected entities
            alternative_intents: List of (intent, confidence) tuples
            parser_raw_confidence: Raw confidence from parser (for weighting)
        
        Returns:
            ComprehensionResult with detailed analysis
        """

        # Calculate base comprehension score
        base_score = confidence

        # Adjust based on entity detection
        entity_score = self._calculate_entity_score(intent, entities, user_message)
        base_score = (base_score * 0.7) + (entity_score * 0.3)

        # Check for keywords/patterns that might need internet search
        needs_internet, search_terms = self._check_internet_relevance(user_message, intent)

        # Determine if clarification is needed
        clarification_needed = base_score < self.confidence_thresholds['medium']
        clarification_question = None

        if clarification_needed and base_score < 0.5:
            clarification_question = self._generate_clarification(user_message, intent, alternative_intents)

        # Determine comprehension level
        comp_level = self._get_comprehension_level(base_score)

        # Build alternative intents list (if not provided)
        if not alternative_intents:
            alternative_intents = []

        # Create reasoning string
        reasoning = self._build_reasoning(user_message, intent, base_score, entity_score, 
                                         needs_internet, clarification_needed)

        return ComprehensionResult(
            intent=intent,
            confidence=confidence,
            comprehension_level=comp_level['name'],
            comprehension_score=base_score,
            entities=entities,
            user_message=user_message,
            needs_internet_search=needs_internet,
            search_terms=search_terms,
            alternative_intents=alternative_intents,
            clarification_needed=clarification_needed,
            clarification_question=clarification_question,
            reasoning=reasoning
        )

    def _calculate_entity_score(self, intent: str, entities: Dict[str, List[str]], 
                               user_message: str) -> float:
        """Calculate score based on entity detection quality"""

        # Expected entities per intent
        entity_expectations = {
            'get_time': ['time_query', 'date'],
            'open_app': ['app'],
            'internet_search': ['search_query'],
            'get_weather': ['date', 'duration'],
            'create_note': ['app'],
            'search_file': ['file', 'path'],
            'system_auto_optimization': [],
            'ai_chat': ['duration'],
        }

        expected = entity_expectations.get(intent, [])

        if not expected:
            # No entities expected for this intent
            return 0.8

        # Count how many expected entities were found
        found_count = sum(1 for entity in expected if entities.get(entity))
        match_score = found_count / len(expected) if expected else 0.8

        # Check for presence of any entities (shows parsing happened)
        has_entities = len(entities) > 1  # More than just _confidence
        has_entities_score = 0.8 if has_entities else 0.5

        return (match_score * 0.6) + (has_entities_score * 0.4)

    def _check_internet_relevance(self, user_message: str, intent: str) -> Tuple[bool, List[str]]:
        """Check if user intent requires internet search"""

        message_lower = user_message.lower()

        # Intent-specific checks
        if intent == 'internet_search':
            # Extract search terms
            search_terms = self._extract_search_terms(user_message)
            return True, search_terms

        # Keyword-based checks
        search_keywords_found = [kw for kw in self.internet_keywords 
                                 if kw in message_lower]

        if search_keywords_found and intent not in ['skill_testing', 'system_status', 'get_time']:
            search_terms = self._extract_search_terms(user_message)
            return True, search_terms

        return False, []

    def _extract_search_terms(self, user_message: str) -> List[str]:
        """Extract potential search terms from user message"""

        # Remove common words
        stop_words = {'de', 'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
                     'para', 'con', 'sin', 'por', 'en', 'a', 'o', 'y', 'que', 'si',
                     'buscar', 'search', 'find', 'busca', 'información', 'info'}

        words = re.findall(r'\b\w+\b', user_message.lower())
        terms = [w for w in words if w not in stop_words and len(w) > 3]

        return terms[:5]  # Return top 5 terms

    def _get_comprehension_level(self, score: float) -> Dict[str, str]:
        """Get comprehension level for a score"""

        # Map score to comprehension level
        if score >= 0.95:
            return {'name': 'Muy claro', 'level': 'VERY_HIGH'}
        elif score >= 0.80:
            return {'name': 'Claro', 'level': 'HIGH'}
        elif score >= 0.60:
            return {'name': 'Moderado', 'level': 'MEDIUM'}
        elif score >= 0.40:
            return {'name': 'Bajo', 'level': 'LOW'}
        else:
            return {'name': 'Muy bajo', 'level': 'VERY_LOW'}

    def _generate_clarification(self, user_message: str, intent: str,
                               alternative_intents: List[Tuple[str, float]]) -> str:
        """Generate clarification question based on ambiguity"""

        # Analyze what's unclear
        clarifications = {
            'internet_search': "¿Quieres buscar información sobre qué tema específicamente?",
            'open_app': "¿Qué aplicación quieres abrir? Tienes: Calculadora, navegador, editor...",
            'search_file': "¿Qué archivo estás buscando? ¿En qué carpeta?",
            'create_note': "¿Qué nota quieres crear? ¿Con qué contenido?",
            'system_auto_optimization': "¿Quieres que optimice la memoria, disco, CPU o todo?",
        }

        # If we have high-confidence alternative, suggest it
        if alternative_intents and alternative_intents[0][1] > 0.3:
            alt_intent, alt_conf = alternative_intents[0]
            return f"¿Quizás quisiste decir '{alt_intent}'? Responde sí o no."

        # Default clarification
        return clarifications.get(intent, f"No estoy seguro qué quieres hacer con '{user_message}'. ¿Puedes ser más específico?")

    def _build_reasoning(self, user_message: str, intent: str, base_score: float,
                        entity_score: float, needs_internet: bool, 
                        clarification_needed: bool) -> str:
        """Build a reasoning string explaining the comprehension"""

        parts = []

        # Confidence assessment
        if base_score > 0.8:
            parts.append(f"Confianza alta en la intención detectada: {intent}")
        elif base_score > 0.6:
            parts.append(f"Moderada confianza en la intención: {intent}")
        else:
            parts.append(f"Baja confianza en la intención: {intent}")

        # Entity coverage
        if entity_score > 0.7:
            parts.append("Las entidades necesarias fueron detectadas correctamente")
        elif entity_score > 0.4:
            parts.append("Algunas entidades esperadas no fueron detectadas")
        else:
            parts.append("La mayoría de entidades esperadas están faltando")

        # Internet relevance
        if needs_internet:
            parts.append("El usuario podría necesitar información de internet para esta tarea")

        # Clarification
        if clarification_needed:
            parts.append("Se recomenda pedir clarificación al usuario")

        return " | ".join(parts)

    def analyze_intent_ambiguity(self, user_message: str, 
                                 parser_results: List[Tuple[str, float]]) -> Dict:
        """Analyze if there's ambiguity in intent detection"""

        if len(parser_results) < 2:
            return {'is_ambiguous': False, 'confidence_gap': 1.0}

        top_intent, top_confidence = parser_results[0]
        second_intent, second_confidence = parser_results[1]

        confidence_gap = top_confidence - second_confidence

        # Ambiguous if gap is < 0.2 (20 percentage points)
        is_ambiguous = confidence_gap < 0.2 and second_confidence > 0.4

        return {
            'is_ambiguous': is_ambiguous,
            'confidence_gap': confidence_gap,
            'top_intent': top_intent,
            'top_confidence': top_confidence,
            'second_intent': second_intent,
            'second_confidence': second_confidence,
            'recommendation': 'Pedir clarificación' if is_ambiguous else 'Proceder con confianza'
        }

    def get_comprehension_report(self, result: ComprehensionResult) -> str:
        """Get human-readable comprehension report"""

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║           NLP COMPREHENSION ANALYSIS REPORT               ║
╠═══════════════════════════════════════════════════════════╣
║ User Message: "{result.user_message}"
║ Detected Intent: {result.intent}
║ Intent Confidence: {result.confidence:.1%}
╠═══════════════════════════════════════════════════════════╣
║ COMPREHENSION SCORING:
║ ├─ Score: {result.comprehension_score:.1%}
║ ├─ Level: {result.comprehension_level}
║ ├─ Confidence: {result.confidence:.1%}
║ └─ Entities: {len(result.entities)} detected
╠═══════════════════════════════════════════════════════════╣
║ ANALYSIS:
║ {result.reasoning}
╠═══════════════════════════════════════════════════════════╣
"""

        if result.needs_internet_search:
            report += f"║ INTERNET SEARCH NEEDED:\n"
            report += f"║ Search Terms: {', '.join(result.search_terms)}\n"
            report += "╠═══════════════════════════════════════════════════════════╣\n"

        if result.clarification_needed:
            report += f"║ CLARIFICATION NEEDED:\n"
            report += f"║ → {result.clarification_question}\n"
            report += "╠═══════════════════════════════════════════════════════════╣\n"

        if result.alternative_intents:
            report += f"║ ALTERNATIVE INTENTS:\n"
            for alt_intent, alt_conf in result.alternative_intents[:3]:
                report += f"║ • {alt_intent}: {alt_conf:.1%}\n"
            report += "╠═══════════════════════════════════════════════════════════╣\n"

        report += "╚═══════════════════════════════════════════════════════════╝\n"
        return report
