# skills/research/internet_search.py
"""
Internet Search Skill - Search Google and retrieve results
Provides web context for answering questions
"""

import requests
from typing import Dict, List, Optional
from urllib.parse import quote


class InternetSearchSkill:
    """Search the internet for information"""
    
    patterns = [
        r".*busca.*",
        r".*search.*",
        r".*encuentra.*",
        r".*google.*",
        r".*web.*",
    ]
    
    def __init__(self):
        self.name = "internet_search"
        self.description = "Search the internet for information"
    
    def run(self, entities, core=None):
        """Execute internet search"""
        
        if not entities.get("query"):
            return {"success": False, "error": "No search query provided"}
        
        query = " ".join(entities["query"]) if isinstance(entities["query"], list) else entities["query"]
        
        results = self.search(query)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google for query (using DuckDuckGo or similar)
        Returns list of results with title, snippet, URL
        """
        results = []
        
        try:
            # Using DuckDuckGo API (no authentication needed)
            url = f"https://duckduckgo.com/?q={quote(query)}&format=json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract results from DuckDuckGo API
                for result in data.get("Results", [])[:num_results]:
                    results.append({
                        "title": result.get("Text", ""),
                        "snippet": result.get("Result", ""),
                        "url": result.get("FirstURL", ""),
                        "source": "DuckDuckGo"
                    })
        
        except Exception as e:
            return [{"error": str(e), "source": "Search API"}]
        
        if not results:
            results.append({
                "message": f"No results found for: {query}",
                "suggestion": "Try a different search term"
            })
        
        return results


class StackOverflowSearchSkill:
    """Search Stack Overflow for programming solutions"""
    
    patterns = [
        r".*stackoverflow.*",
        r".*error.*",
        r".*problema.*",
        r".*solution.*",
        r".*coding.*",
    ]
    
    def __init__(self):
        self.name = "stackoverflow_search"
        self.description = "Search Stack Overflow for programming help"
    
    def run(self, entities, core=None):
        """Search Stack Overflow"""
        
        if not entities.get("query"):
            return {"success": False, "error": "No query provided"}
        
        query = " ".join(entities["query"]) if isinstance(entities["query"], list) else entities["query"]
        
        results = self.search(query)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "platform": "Stack Overflow"
        }
    
    def search(self, query: str, num_results: int = 3) -> List[Dict]:
        """Search Stack Overflow API"""
        results = []
        
        try:
            # Stack Overflow API
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": query,
                "order": "desc",
                "sort": "relevance",
                "site": "stackoverflow",
                "pagesize": num_results
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("items", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "score": item.get("score", 0),
                        "answers": item.get("answer_count", 0),
                        "url": item.get("link", ""),
                        "tags": item.get("tags", []),
                        "views": item.get("view_count", 0)
                    })
        
        except Exception as e:
            return [{"error": str(e), "source": "Stack Overflow API"}]
        
        return results


class GitHubSearchSkill:
    """Search GitHub for repositories and code"""
    
    patterns = [
        r".*github.*",
        r".*repo.*",
        r".*código.*",
        r".*library.*",
    ]
    
    def __init__(self):
        self.name = "github_search"
        self.description = "Search GitHub for repositories and code"
    
    def run(self, entities, core=None):
        """Search GitHub"""
        
        if not entities.get("query"):
            return {"success": False, "error": "No query provided"}
        
        query = " ".join(entities["query"]) if isinstance(entities["query"], list) else entities["query"]
        
        results = self.search(query)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "platform": "GitHub"
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search GitHub API"""
        results = []
        
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": num_results
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get("items", [])[:num_results]:
                    results.append({
                        "name": repo.get("name", ""),
                        "description": repo.get("description", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language", ""),
                        "url": repo.get("html_url", ""),
                        "forks": repo.get("forks_count", 0)
                    })
        
        except Exception as e:
            return [{"error": str(e), "source": "GitHub API"}]
        
        return results
