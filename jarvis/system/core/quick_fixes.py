"""
Jarvis Quick Fixes - Critical methods for v0.0.4
Adds missing functionality to JarvisCore for immediate operation
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class JarvisQuickFixes:
    """Mixin to add critical missing methods to JarvisCore"""
    
    def get_available_skills(self) -> List[Dict]:
        """Get list of all available skills"""
        try:
            skills_list = []
            
            # Get skills from dispatcher registry
            if hasattr(self, 'skill_dispatcher') and hasattr(self.skill_dispatcher, 'skills'):
                for skill_name, skill_class in self.skill_dispatcher.skills.items():
                    skills_list.append({
                        'name': skill_name,
                        'class': skill_class.__name__ if hasattr(skill_class, '__name__') else str(skill_class),
                        'description': skill_class.__doc__ if hasattr(skill_class, '__doc__') else f"Skill: {skill_name}"
                    })
            
            if not skills_list:
                # Fallback: hardcoded known skills for v0.0.4
                skills_list = [
                    {'name': 'get_time', 'class': 'GetTimeSkill', 'description': 'Get current time'},
                    {'name': 'open_app', 'class': 'OpenAppSkill', 'description': 'Open application'},
                    {'name': 'internet_search', 'class': 'InternetSearchSkill', 'description': 'Search internet'},
                    {'name': 'search_file', 'class': 'SearchFileSkill', 'description': 'Search files'},
                    {'name': 'create_note', 'class': 'CreateNoteSkill', 'description': 'Create note'},
                    {'name': 'system_status', 'class': 'SystemStatusSkill', 'description': 'Get system status'},
                    {'name': 'system_auto_optimization', 'class': 'SystemAutoOptSkill', 'description': 'Optimize system'},
                    {'name': 'summarize_recent_activity', 'class': 'SummarizeActivitySkill', 'description': 'Summarize activity'},
                    {'name': 'analyze_session_value', 'class': 'AnalyzeSessionSkill', 'description': 'Analyze session'},
                    {'name': 'skill_testing', 'class': 'SkillTestingSkill', 'description': 'Test skills'},
                    {'name': 'web_browser', 'class': 'WebBrowserSkill', 'description': 'Web browser'},
                    {'name': 'ai_chat', 'class': 'AIChatSkill', 'description': 'AI conversation'},
                ]
            
            return sorted(skills_list, key=lambda x: x['name'])
            
        except Exception as e:
            logger.error(f"Error getting available skills: {e}")
            return []
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get detailed info about a specific skill"""
        try:
            all_skills = self.get_available_skills()
            for skill in all_skills:
                if skill['name'].lower() == skill_name.lower():
                    return skill
            return None
        except Exception as e:
            logger.error(f"Error getting skill info for {skill_name}: {e}")
            return None
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        try:
            status = {
                'timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S'),
                'uptime_seconds': __import__('time').time() - self.start_time,
                'state': self.state.get() if hasattr(self, 'state') else 'UNKNOWN',
                'components_ok': len(self._components_initialized) if hasattr(self, '_components_initialized') else 0,
                'components_failed': len(self._components_failed) if hasattr(self, '_components_failed') else 0,
                'session_id': self.session_manager.current_session.id if hasattr(self, 'session_manager') else None,
                'mode': self.mode_controller.current_mode.value if hasattr(self, 'mode_controller') else 'UNKNOWN'
            }
            return status
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def toggle_debug_mode(self) -> bool:
        """Toggle debug mode ON/OFF and return new state"""
        try:
            current_debug = getattr(self, '_debug_mode', False)
            new_debug = not current_debug
            self._debug_mode = new_debug
            
            # Also update NLU if it supports debug
            if hasattr(self, 'nlu') and hasattr(self.nlu, 'debug'):
                self.nlu.debug = new_debug
            
            logger.info(f"Debug mode toggled: {new_debug}")
            return new_debug
            
        except Exception as e:
            logger.error(f"Error toggling debug mode: {e}")
            return False
    
    def get_debug_status(self) -> bool:
        """Get current debug mode status"""
        return getattr(self, '_debug_mode', False)
    
    def submit_background_task(self, task_id: str, task_name: str, function, args=None, kwargs=None, priority=0) -> str:
        """Submit a task to background task manager"""
        try:
            if hasattr(self, 'task_manager'):
                return self.task_manager.submit_task(
                    task_id=task_id,
                    name=task_name,
                    function=function,
                    args=args or (),
                    kwargs=kwargs or {},
                    priority=priority
                )
            else:
                logger.warning("BackgroundTaskManager not available")
                return None
        except Exception as e:
            logger.error(f"Error submitting background task: {e}")
            return None
    
    def get_background_tasks(self) -> List[Dict]:
        """Get list of active background tasks"""
        try:
            if hasattr(self, 'task_manager'):
                return self.task_manager.get_all_tasks()
            return []
        except Exception as e:
            logger.error(f"Error getting background tasks: {e}")
            return []
    
    def get_process_monitor_status(self) -> Dict:
        """Get current process monitor status"""
        try:
            if hasattr(self, 'process_monitor'):
                summary = self.process_monitor.get_system_summary()
                return {
                    'processes': summary['total_processes'],
                    'cpu_percent': summary['cpu_usage_percent'],
                    'memory_percent': summary['memory_usage_percent'],
                    'disk_percent': summary['disk_usage_percent']
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting process monitor status: {e}")
            return {}
    
    def enable_constant_monitoring(self) -> bool:
        """Enable constant PC monitoring"""
        try:
            if hasattr(self, 'process_monitor'):
                # Start background thread for constant monitoring
                import threading
                
                def monitor_loop():
                    import time
                    while getattr(self, '_monitoring_enabled', True):
                        try:
                            snapshot = self.process_monitor.scan_processes()
                            
                            # Check for critical conditions
                            if snapshot.cpu_usage > 80:
                                logger.warning(f"HIGH CPU: {snapshot.cpu_usage:.1f}%")
                            if snapshot.memory_usage > 90:
                                logger.warning(f"HIGH MEMORY: {snapshot.memory_usage:.1f}%")
                            
                            time.sleep(5)  # Check every 5 seconds
                        except Exception as e:
                            logger.error(f"Monitoring error: {e}")
                
                self._monitoring_enabled = True
                monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
                monitor_thread.start()
                logger.info("Constant PC monitoring enabled")
                return True
            return False
        except Exception as e:
            logger.error(f"Error enabling constant monitoring: {e}")
            return False
    
    def disable_constant_monitoring(self) -> bool:
        """Disable constant PC monitoring"""
        try:
            self._monitoring_enabled = False
            logger.info("Constant PC monitoring disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling constant monitoring: {e}")
            return False


# Export the mixin so it can be used with JarvisCore
__all__ = ['JarvisQuickFixes']
