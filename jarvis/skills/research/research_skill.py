# skills/research_skill.py
"""
Research & Data Gathering Skill for JarvisAI v0.0.4
Searches local data first, then web data with safe parsing
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import quote
import time


class ResearchSkill:
    """
    Safe research skill that gathers information from local and web sources
    Never executes external commands, only reads data
    """

    patterns = [
        r"\b(investigar|research|buscar|search|encontrar|find)\b.*\b(informacion|information|datos|data|acerca de|about)\b",
        r"\b(que sabes|what do you know|dime sobre|tell me about)\b",
        r"\b(busqueda|search|query)\b.*\b(web|internet|online)\b"
    ]

    entity_hints = {
        "query": {"pattern": r"(?:buscar|search|investigar|research)\s+(.+)"},
        "topic": {"pattern": r"(?:acerca de|about|sobre|sobre)\s+(.+)"}
    }

    def run(self, entities, core):
        """Perform research based on user query"""

        # Extract query from entities
        query = self._extract_query(entities)

        if not query:
            return {
                "success": False,
                "error": "No pude identificar qué investigar. Especifica mejor tu consulta."
            }

        # Research pipeline: local first, then web
        results = {
            "query": query,
            "local_results": self._search_local(query, core),
            "web_results": self._search_web_safe(query),
            "sources": [],
            "confidence": 0.0
        }

        # Calculate confidence based on results
        results["confidence"] = self._calculate_confidence(results)

        # Save research for learning
        self._save_research(core, results)

        # Format response
        response = self._format_research_response(results)

        return {
            "success": True,
            "result": response,
            "research_data": results
        }

    def _extract_query(self, entities) -> Optional[str]:
        """Extract search query from entities"""
        # Try different entity keys
        for key in ['query', 'topic', 'search_query']:
            if entities.get(key):
                query = entities[key]
                if isinstance(query, list) and query:
                    return str(query[0])
                return str(query)

        # Fallback: reconstruct from raw entities
        if entities.get('app'):
            return f"aplicación {entities['app']}"
        if entities.get('file'):
            return f"archivo {entities['file']}"

        return None

    def _search_local(self, query: str, core) -> List[Dict[str, Any]]:
        """Search local JarvisAI data and logs"""
        results = []

        try:
            # Search in command history
            history = getattr(core, 'command_history', [])
            relevant_commands = [
                cmd for cmd in history[-100:]  # Last 100 commands
                if query.lower() in cmd.lower()
            ]

            if relevant_commands:
                results.append({
                    "type": "command_history",
                    "title": f"Comandos relacionados con '{query}'",
                    "content": f"Encontré {len(relevant_commands)} comandos similares en tu historial",
                    "data": relevant_commands[:5],  # Show first 5
                    "source": "local_history",
                    "confidence": 0.8
                })

            # Search in data collector insights
            if hasattr(core, 'data_collector'):
                suggestions = core.data_collector.get_suggestions()
                relevant_suggestions = [
                    s for s in suggestions
                    if query.lower() in s.lower()
                ]

                if relevant_suggestions:
                    results.append({
                        "type": "usage_patterns",
                        "title": "Patrones de uso relacionados",
                        "content": f"Basado en tu uso: {', '.join(relevant_suggestions[:3])}",
                        "data": relevant_suggestions,
                        "source": "usage_analytics",
                        "confidence": 0.7
                    })

        except Exception as e:
            core.logger.logger.warning(f"Error in local search: {e}")

        return results

    def _search_web_safe(self, query: str) -> List[Dict[str, Any]]:
        """Safe web search using requests (no external commands)"""
        results = []

        try:
            # Use DuckDuckGo instant answers API (safe, no API key needed)
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"

            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()

            # Extract instant answer if available
            if data.get('Answer'):
                results.append({
                    "type": "instant_answer",
                    "title": data.get('Answer'),
                    "content": data.get('Answer'),
                    "source": "duckduckgo_instant",
                    "confidence": 0.9
                })

            # Extract abstract if available
            elif data.get('AbstractText'):
                results.append({
                    "type": "web_abstract",
                    "title": data.get('Heading', query),
                    "content": data.get('AbstractText')[:500] + "..." if len(data.get('AbstractText', '')) > 500 else data.get('AbstractText', ''),
                    "source": "duckduckgo_abstract",
                    "confidence": 0.8
                })

            # Extract related topics
            if data.get('RelatedTopics'):
                topics = data['RelatedTopics'][:3]  # First 3 topics
                for topic in topics:
                    if topic.get('Text'):
                        results.append({
                            "type": "related_topic",
                            "title": topic.get('Text', '')[:100],
                            "content": topic.get('Text', ''),
                            "source": "duckduckgo_related",
                            "confidence": 0.6
                        })

        except requests.exceptions.RequestException as e:
            results.append({
                "type": "error",
                "title": "Error de conexión web",
                "content": f"No pude acceder a información web: {str(e)}",
                "source": "web_error",
                "confidence": 0.0
            })
        except Exception as e:
            results.append({
                "type": "error",
                "title": "Error en búsqueda web",
                "content": f"Error inesperado: {str(e)}",
                "source": "web_error",
                "confidence": 0.0
            })

        return results

    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence in research results"""
        if not results['local_results'] and not results['web_results']:
            return 0.0

        # Weight local results higher than web results
        local_weight = len(results['local_results']) * 0.3
        web_weight = len(results['web_results']) * 0.2

        # Bonus for instant answers
        instant_bonus = 0.2 if any(r.get('type') == 'instant_answer' for r in results['web_results']) else 0.0

        confidence = min(1.0, local_weight + web_weight + instant_bonus)
        return round(confidence, 2)

    def _save_research(self, core, results: Dict[str, Any]):
        """Save research results for learning"""
        try:
            data_dir = os.path.join(os.path.expanduser("~"), "Desktop", "JarvisData", "research")
            os.makedirs(data_dir, exist_ok=True)

            filename = os.path.join(data_dir, f"research_{int(time.time())}.json")

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            core.logger.logger.warning(f"Could not save research: {e}")

    def _format_research_response(self, results: Dict[str, Any]) -> str:
        """Format research results into readable response"""
        response_parts = [f"🔍 Investigación sobre: '{results['query']}'\n"]

        # Confidence indicator
        confidence = results['confidence']
        if confidence > 0.8:
            response_parts.append("🟢 Alta confianza en los resultados")
        elif confidence > 0.5:
            response_parts.append("🟡 Confianza media en los resultados")
        else:
            response_parts.append("🔴 Baja confianza - resultados limitados")

        # Local results
        local_results = results['local_results']
        if local_results:
            response_parts.append(f"\n📁 Información local ({len(local_results)} resultados):")
            for result in local_results[:3]:  # Show top 3
                response_parts.append(f"  • {result['title']}")
                if len(result['content']) < 200:
                    response_parts.append(f"    {result['content']}")

        # Web results
        web_results = results['web_results']
        if web_results:
            response_parts.append(f"\n🌐 Información web ({len(web_results)} resultados):")
            for result in web_results[:3]:  # Show top 3
                if result['type'] != 'error':
                    response_parts.append(f"  • {result['title']}")
                    if len(result['content']) < 150:
                        response_parts.append(f"    {result['content']}")

        # No results
        if not local_results and not web_results:
            response_parts.append("\n❌ No encontré información relevante sobre este tema.")

        return "\n".join(response_parts)