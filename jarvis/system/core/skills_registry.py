# system/core/skills_registry.py
"""
Skills Registry for JarvisAI Core
Manages skill registration and initialization
"""

from typing import Dict, Type, TYPE_CHECKING
if TYPE_CHECKING:
    from .core import JarvisCore

# Import all available skills
from skills.productivity.open_app import OpenAppSkill
from skills.system.get_time import GetTimeSkill
from skills.system.system_status import SystemStatusSkill
from skills.productivity.create_note import CreateNoteSkill
from skills.research.search_file import SearchFileSkill
from skills.research.summarize_recent_activity import SummarizeRecentActivitySkill
from skills.research.summarize_last_session import SummarizeLastSessionSkill
from skills.analysis.analyze_session_value import AnalyzeSessionValueSkill
from skills.analysis.research_and_contextualize import ResearchAndContextualizeSkill
from skills.system.analyze_system_health import AnalyzeSystemHealthSkill
from skills.system.what_do_you_know_about_me import WhatDoYouKnowAboutMeSkill
from skills.analysis.evaluate_user_session import EvaluateUserSessionSkill
from skills.system.system_auto_optimization import SystemAutoOptimizationSkill
from skills.automation.auto_programming import AutoProgrammingSkill


class SkillsRegistry:
    """
    Registry for all available skills in JarvisAI
    """

    # Base skills registry - always available
    BASE_SKILLS: Dict[str, Type] = {
        "open_app": OpenAppSkill,
        "get_time": GetTimeSkill,
        "system_status": SystemStatusSkill,
        "create_note": CreateNoteSkill,
        "search_file": SearchFileSkill,
        "summarize_recent_activity": SummarizeRecentActivitySkill,
    }

    # Advanced skills registry - may require additional dependencies
    ADVANCED_SKILLS: Dict[str, Type] = {
        "summarize_last_session": SummarizeLastSessionSkill,
        "analyze_session_value": AnalyzeSessionValueSkill,
        "research_and_contextualize": ResearchAndContextualizeSkill,
        "analyze_system_health": AnalyzeSystemHealthSkill,
        "what_do_you_know_about_me": WhatDoYouKnowAboutMeSkill,
        "evaluate_user_session": EvaluateUserSessionSkill,
        "system_auto_optimization": SystemAutoOptimizationSkill,
        "auto_programming": AutoProgrammingSkill,
    }

    def __init__(self, core: 'JarvisCore'):
        self.core = core
        self._registered_skills: Dict[str, object] = {}

    def register_all_skills(self):
        """
        Register all available skills based on configuration
        """
        # Always register base skills
        for name, skill_cls in self.BASE_SKILLS.items():
            self._register_skill(name, skill_cls)

        # Register advanced skills if enabled
        if self.core.config.get("advanced_skills", True):
            for name, skill_cls in self.ADVANCED_SKILLS.items():
                try:
                    self._register_skill(name, skill_cls)
                except Exception as e:
                    self.core.logger.logger.warning(f"Failed to register advanced skill '{name}': {e}")

        self.core.logger.logger.info(f"Registered {len(self._registered_skills)} skills")

    def _register_skill(self, name: str, skill_cls: Type):
        """
        Register a single skill with proper instantiation
        """
        try:
            # Handle skills that need special initialization
            if name == "research_and_contextualize":
                skill_instance = skill_cls(self.core.storage, self.core.llm_manager)
            elif name in ["analyze_system_health", "system_auto_optimization"]:
                skill_instance = skill_cls(self.core.logger.logger)
            elif name in ["what_do_you_know_about_me", "evaluate_user_session", "auto_programming"]:
                skill_instance = skill_cls(self.core.storage, self.core.active_learning, self.core.logger.logger)
            else:
                # Check if it's already instantiated (has run method)
                if hasattr(skill_cls, 'run'):
                    skill_instance = skill_cls
                else:
                    # Instantiate the class
                    skill_instance = skill_cls()

            # Register with dispatcher
            self.core.skill_dispatcher.register(name, skill_instance)
            self._registered_skills[name] = skill_instance

            self.core.logger.logger.debug(f"[SKILLS] Registered skill: {name}")

        except Exception as e:
            self.core.logger.logger.error(f"Failed to register skill '{name}': {e}")
            raise

    def get_registered_skills(self) -> Dict[str, object]:
        """Get all registered skill instances"""
        return self._registered_skills.copy()

    def get_skill_names(self) -> list:
        """Get list of registered skill names"""
        return list(self._registered_skills.keys())

    def reload_skill(self, name: str):
        """
        Reload a specific skill (useful for development)
        """
        if name in self.BASE_SKILLS:
            skill_cls = self.BASE_SKILLS[name]
        elif name in self.ADVANCED_SKILLS:
            skill_cls = self.ADVANCED_SKILLS[name]
        else:
            raise ValueError(f"Unknown skill: {name}")

        # Remove old registration
        if name in self._registered_skills:
            del self._registered_skills[name]

        # Re-register
        self._register_skill(name, skill_cls)
        self.core.logger.logger.info(f"Reloaded skill: {name}")