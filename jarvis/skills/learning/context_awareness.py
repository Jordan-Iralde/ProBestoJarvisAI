"""
Smart Context Awareness System
Learns from user interaction patterns to provide more relevant responses and predictions
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class ContextAwareness:
    """
    Smart Context Awareness Engine
    - Tracks user interaction patterns
    - Identifies common tasks and times
    - Predicts next actions
    - Personalizes responses
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "..", "data")
        self.context_file = os.path.join(self.data_dir, "context_awareness.json")
        self.data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load context data from disk"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "user_preferences": {},
            "time_patterns": defaultdict(list),
            "skill_frequency": defaultdict(int),
            "last_interactions": [],
            "context_chain": [],
            "predictions": []
        }
    
    def _save_data(self):
        """Save context data to disk"""
        os.makedirs(self.data_dir, exist_ok=True)
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
        except:
            pass
    
    def record_interaction(self, skill_name: str, input_text: str, output_text: str, 
                          timestamp: datetime = None) -> None:
        """Record an interaction for pattern analysis"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Track skill frequency
        self.data["skill_frequency"][skill_name] = self.data["skill_frequency"].get(skill_name, 0) + 1
        
        # Track time patterns
        hour = timestamp.hour
        time_key = f"hour_{hour:02d}"
        self.data["time_patterns"][time_key] = self.data["time_patterns"].get(time_key, [])
        self.data["time_patterns"][time_key].append(skill_name)
        
        # Track interaction chain
        interaction = {
            "timestamp": timestamp.isoformat(),
            "skill": skill_name,
            "input": input_text[:100],  # First 100 chars
            "hour": hour,
            "day": timestamp.strftime("%A")
        }
        
        self.data["last_interactions"].append(interaction)
        
        # Keep last 1000 interactions
        if len(self.data["last_interactions"]) > 1000:
            self.data["last_interactions"] = self.data["last_interactions"][-1000:]
        
        self._save_data()
    
    def get_context_summary(self) -> Dict:
        """Get current context summary"""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A")
        
        # Most used skills
        top_skills = sorted(
            self.data["skill_frequency"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Skills used at this hour
        time_key = f"hour_{hour:02d}"
        hourly_skills = self.data["time_patterns"].get(time_key, [])
        
        return {
            "current_hour": hour,
            "current_day": day,
            "top_skills": [{"name": s[0], "usage_count": s[1]} for s in top_skills],
            "likely_next_skills": list(set(hourly_skills[-5:])) if hourly_skills else [],
            "total_interactions": len(self.data["last_interactions"]),
        }
    
    def predict_next_action(self, recent_skills: List[str] = None) -> Optional[str]:
        """Predict the user's next action based on patterns"""
        if not self.data["last_interactions"]:
            return None
        
        # Get last 5 interactions
        recent = self.data["last_interactions"][-5:] if len(self.data["last_interactions"]) >= 5 else self.data["last_interactions"]
        
        # Find skills at similar time
        now = datetime.now()
        hour = now.hour
        time_key = f"hour_{hour:02d}"
        
        hourly_skills = self.data["time_patterns"].get(time_key, [])
        if hourly_skills:
            # Return most common skill at this hour
            from collections import Counter
            skill_counts = Counter(hourly_skills)
            return skill_counts.most_common(1)[0][0]
        
        return None
    
    def get_personalized_message(self, base_message: str) -> str:
        """Add personalization to messages based on context"""
        context = self.get_context_summary()
        
        # Add contextual hints
        if context["top_skills"]:
            if context["total_interactions"] > 100:
                prefix = "I see you often use " + ", ".join([s["name"] for s in context["top_skills"][:2]])
                return f"{prefix}. {base_message}"
        
        return base_message
    
    def identify_workflow(self) -> Optional[Dict]:
        """Identify common workflow patterns"""
        if len(self.data["last_interactions"]) < 10:
            return None
        
        # Analyze last 20 interactions for patterns
        recent = self.data["last_interactions"][-20:]
        skills_sequence = [i["skill"] for i in recent]
        
        # Look for repeating patterns
        from collections import Counter
        transitions = []
        for i in range(len(skills_sequence) - 1):
            transitions.append((skills_sequence[i], skills_sequence[i+1]))
        
        if transitions:
            transition_counts = Counter(transitions)
            most_common = transition_counts.most_common(3)
            
            return {
                "type": "workflow",
                "pattern": [(t[0][0], t[0][1], t[1]) for t in most_common],
                "frequency": most_common
            }
        
        return None
    
    def suggest_optimization(self) -> Optional[str]:
        """Suggest optimization based on usage patterns"""
        context = self.get_context_summary()
        
        # If user uses same 2 skills repeatedly, suggest automation
        top_2 = context["top_skills"][:2]
        if len(top_2) >= 2 and top_2[0]["usage_count"] > 20:
            return f"Consider automating {top_2[0]['name']} + {top_2[1]['name']} workflow for faster execution"
        
        # If user only uses few skills, suggest exploring more
        if len(context["top_skills"]) < 3 and context["total_interactions"] > 50:
            return "Try exploring more skills for enhanced productivity"
        
        return None


class ContextAwarenessSkill:
    """Skill wrapper for context awareness"""
    
    def __init__(self):
        self.engine = ContextAwareness()
        self.name = "context_awareness"
    
    def execute(self, user_input: str, core=None) -> str:
        """Handle context awareness requests"""
        
        user_input = user_input.lower()
        
        if "suggest" in user_input or "optimize" in user_input:
            suggestion = self.engine.suggest_optimization()
            return suggestion or "No optimization suggestions at the moment"
        
        if "pattern" in user_input or "workflow" in user_input:
            workflow = self.engine.identify_workflow()
            if workflow:
                return f"I've identified your workflow: {workflow['pattern']}"
            return "Not enough data yet to identify patterns"
        
        if "predict" in user_input or "next" in user_input:
            prediction = self.engine.predict_next_action()
            return f"Based on patterns, you might want to use {prediction} next" if prediction else "No predictions yet"
        
        # Default: show context summary
        context = self.engine.get_context_summary()
        return f"Context: {context['total_interactions']} total interactions. Top skills: {', '.join([s['name'] for s in context['top_skills']])}"
