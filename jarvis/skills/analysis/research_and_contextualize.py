# skills/research_and_contextualize.py
"""
Research and Contextualize Skill - Autonomous information gathering
Searches, summarizes and stores knowledge for future use.
"""

import time
from typing import Dict, Any, Optional
# import requests  # Commented out for now


class ResearchAndContextualizeSkill:
    """
    Skill for autonomous research and knowledge contextualization.
    Searches web/docs, summarizes, and stores structured knowledge.
    """

    def __init__(self, storage=None, llm_manager=None):
        self.storage = storage
        self.llm_manager = llm_manager

    def run(self, query: str) -> Dict[str, Any]:
        """
        Research a topic, contextualize with existing knowledge, and store insights.

        Args:
            query: The research topic/query

        Returns:
            Structured research results with summary and stored knowledge
        """
        try:
            # Step 1: Search for information
            search_results = self._search_web(query)

            if not search_results:
                return {
                    "success": False,
                    "error": "No se encontraron resultados de búsqueda",
                    "query": query
                }

            # Step 2: Extract and summarize key information
            summary = self._summarize_results(query, search_results)

            # Step 3: Contextualize with existing knowledge
            context = self._find_related_knowledge(query)

            # Step 4: Generate structured knowledge
            knowledge = self._create_structured_knowledge(query, summary, context)

            # Step 5: Store for future use
            if self.storage:
                self._store_knowledge(knowledge)

            return {
                "success": True,
                "query": query,
                "summary": summary,
                "key_findings": knowledge.get("key_findings", []),
                "recommendations": knowledge.get("recommendations", []),
                "stored": bool(self.storage),
                "confidence": knowledge.get("confidence", 0.7)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error en investigación: {str(e)}",
                "query": query
            }

    def _search_web(self, query: str) -> list:
        """
        Perform web search using mock implementation (no external dependencies).
        Returns mock search results for testing.
        """
        # Mock search results for testing
        mock_results = [
            {
                "title": f"Guía completa sobre {query}",
                "url": f"https://example.com/guide-{query.replace(' ', '-')}",
                "snippet": f"Información detallada y actualizada sobre {query}"
            },
            {
                "title": f"Tutorial: {query} paso a paso",
                "url": f"https://tutorial.com/{query.replace(' ', '-')}",
                "snippet": f"Aprende {query} con este tutorial completo"
            },
            {
                "title": f"Mejores prácticas para {query}",
                "url": f"https://bestpractices.com/{query.replace(' ', '-')}",
                "snippet": f"Descubre las mejores prácticas y consejos para {query}"
            }
        ]

        return mock_results[:3]  # Return top 3 mock results

    def _summarize_results(self, query: str, results: list) -> str:
        """
        Summarize search results using LLM if available, otherwise basic summary.
        """
        if not results:
            return "No se encontraron resultados para resumir."

        if self.llm_manager:
            # Use LLM for intelligent summarization
            prompt = f"""
            Basado en estos resultados de búsqueda para la consulta "{query}",
            proporciona un resumen conciso y útil en español:

            Resultados:
            {chr(10).join([f"- {r['title']}" for r in results])}

            Resumen:
            """

            try:
                summary_response = self.llm_manager.generate_response(prompt)
                return summary_response.strip()
            except:
                pass

        # Fallback: Basic summary
        titles = [r['title'] for r in results[:3]]
        return f"Encontré información sobre: {', '.join(titles)}. Recomiendo investigar estos temas para más detalles."

    def _find_related_knowledge(self, query: str) -> list:
        """
        Find related knowledge from stored conversations and facts.
        """
        if not self.storage:
            return []

        # Get recent conversations and filter for related content
        recent_convs = self.storage.get_last_conversations(20)

        # Simple keyword matching for related conversations
        query_words = set(query.lower().split())
        related_convs = []

        for conv in recent_convs:
            conv_text = f"{conv['user_input']} {conv['response']}".lower()
            conv_words = set(conv_text.split())

            # Check for word overlap
            if query_words & conv_words:
                related_convs.append(conv)
                if len(related_convs) >= 5:  # Limit to 5
                    break

        # Extract relevant context
        context = []
        for conv in related_convs:
            context.append({
                "type": "conversation",
                "content": f"Usuario: {conv['user_input']} | Jarvis: {conv['response']}",
                "timestamp": conv["timestamp"]
            })

        return context

    def _create_structured_knowledge(self, query: str, summary: str, context: list) -> Dict[str, Any]:
        """
        Create structured knowledge object for storage.
        """
        knowledge = {
            "topic": query,
            "summary": summary,
            "key_findings": [],
            "recommendations": [],
            "related_context": context,
            "timestamp": time.time(),
            "confidence": 0.7
        }

        # Extract key findings (basic NLP)
        sentences = summary.split('.')
        knowledge["key_findings"] = [s.strip() for s in sentences if s.strip()][:3]

        # Generate recommendations
        if "optimizar" in query.lower() or "mejorar" in query.lower():
            knowledge["recommendations"].append("Considerar implementar los hallazgos encontrados")
        elif "problema" in query.lower() or "error" in query.lower():
            knowledge["recommendations"].append("Revisar las soluciones propuestas en los resultados")
        else:
            knowledge["recommendations"].append("Explorar los temas relacionados encontrados")

        return knowledge

    def _store_knowledge(self, knowledge: Dict[str, Any]):
        """
        Store structured knowledge in the system.
        """
        try:
            # Store as a special conversation or fact
            fact_text = f"Conocimiento investigado: {knowledge['topic']} - {knowledge['summary'][:200]}..."

            self.storage.save_conversation(
                user_input=f"[RESEARCH] {knowledge['topic']}",
                response=fact_text,
                source="research"
            )

        except Exception as e:
            print(f"Error almacenando conocimiento: {e}")

    def get_stored_knowledge(self, topic: str) -> list:
        """
        Retrieve stored knowledge about a topic.
        """
        if not self.storage:
            return []

        # Get recent conversations and filter for research results
        recent_convs = self.storage.get_last_conversations(50)

        research_results = []
        for conv in recent_convs:
            if "[RESEARCH]" in conv["user_input"] and topic.lower() in conv["user_input"].lower():
                research_results.append({
                    "topic": topic,
                    "summary": conv["response"],
                    "timestamp": conv["timestamp"]
                })

        return research_results