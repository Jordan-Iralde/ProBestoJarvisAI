"""
Patch file for engine.py - Adds v0.0.4 integration methods
Apply this after the JarvisCore class definition

This script adds the missing methods to JarvisCore without modifying the existing code.
To use: Import these methods into engine.py or use as a mixin
"""

# These methods should be added to the JarvisCore class in engine.py
# Location: After the reload_config method (around line 487)

def get_available_skills_patch(self):
    """Get list of all available skills"""
    try:
        skills_list = []
        
        # Get skills from dispatcher registry
        if hasattr(self, 'skill_dispatcher') and hasattr(self.skill_dispatcher, 'skills'):
            for skill_name, skill_instance in self.skill_dispatcher.skills.items():
                skill_doc = skill_instance.__doc__ if hasattr(skill_instance, '__doc__') else f"Skill: {skill_name}"
                skills_list.append({
                    'name': skill_name,
                    'class': skill_instance.__class__.__name__,
                    'description': skill_doc
                })
        
        return sorted(skills_list, key=lambda x: x['name'])
        
    except Exception as e:
        self.logger.logger.error(f"Error getting available skills: {e}")
        return []


def get_skill_info_patch(self, skill_name: str):
    """Get detailed info about a specific skill"""
    try:
        all_skills = self.get_available_skills()
        for skill in all_skills:
            if skill['name'].lower() == skill_name.lower():
                return skill
        return None
    except Exception as e:
        self.logger.logger.error(f"Error getting skill info for {skill_name}: {e}")
        return None


def get_system_status_patch(self):
    """Get current system status with comprehensive info"""
    try:
        import psutil
        import os
        
        status = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'uptime_seconds': __import__('time').time() - self.start_time,
            'state': self.state.get() if hasattr(self, 'state') else 'UNKNOWN',
            'components_ok': len(self._components_initialized) if hasattr(self, '_components_initialized') else 0,
            'components_failed': len(self._components_failed) if hasattr(self, '_components_failed') else 0,
            'session_id': self.session_manager.current_session.id if hasattr(self, 'session_manager') and hasattr(self.session_manager, 'current_session') else None,
            'mode': self.mode_controller.current_mode.value if hasattr(self, 'mode_controller') else 'UNKNOWN',
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'processes': len(psutil.pids())
            },
            'debug_mode': getattr(self, '_debug_mode', False)
        }
        return status
    except Exception as e:
        self.logger.logger.error(f"Error getting system status: {e}")
        return {'error': str(e)}


def toggle_debug_mode_patch(self):
    """Toggle debug mode ON/OFF and return new state"""
    try:
        current_debug = getattr(self, '_debug_mode', False)
        new_debug = not current_debug
        self._debug_mode = new_debug
        
        # Also update NLU if it supports debug
        if hasattr(self, 'nlu') and hasattr(self.nlu, 'debug'):
            self.nlu.debug = new_debug
        
        self.logger.logger.info(f"Debug mode toggled: {'ON' if new_debug else 'OFF'}")
        return new_debug
        
    except Exception as e:
        self.logger.logger.error(f"Error toggling debug mode: {e}")
        return False


def get_debug_status_patch(self):
    """Get current debug mode status"""
    return getattr(self, '_debug_mode', False)


def init_v004_integration_patch(self):
    """Initialize v0.0.4 integration after boot"""
    try:
        from .v004_integration import integrate_v004_into_engine
        self.integration_layer = integrate_v004_into_engine(self)
        self.logger.logger.info("✓ v0.0.4 integration initialized")
    except Exception as e:
        self.logger.logger.warning(f"Could not initialize v0.0.4 integration: {e}")
        self.integration_layer = None


def submit_background_task_patch(self, task_id: str, task_name: str, function, args=None, kwargs=None, priority=0):
    """Submit a task to background task manager"""
    try:
        if hasattr(self, 'task_manager') and self.task_manager:
            return self.task_manager.submit_task(
                task_id=task_id,
                name=task_name,
                function=function,
                args=args or (),
                kwargs=kwargs or {},
                priority=priority
            )
        else:
            self.logger.logger.warning("BackgroundTaskManager not available, executing synchronously")
            return function(*( args or ()), **{kwargs or {}})
    except Exception as e:
        self.logger.logger.error(f"Error submitting background task: {e}")
        return None


def get_background_tasks_patch(self):
    """Get list of active background tasks"""
    try:
        if hasattr(self, 'task_manager') and self.task_manager:
            return self.task_manager.get_all_tasks()
        return []
    except Exception as e:
        self.logger.logger.error(f"Error getting background tasks: {e}")
        return []


# Usage instruction:
# In engine.py, after the class definition or in __init__, add:
# 
# JarvisCore.get_available_skills = get_available_skills_patch
# JarvisCore.get_skill_info = get_skill_info_patch
# JarvisCore.get_system_status = get_system_status_patch
# JarvisCore.toggle_debug_mode = toggle_debug_mode_patch
# JarvisCore.get_debug_status = get_debug_status_patch
# JarvisCore.init_v004_integration = init_v004_integration_patch
# JarvisCore.submit_background_task = submit_background_task_patch
# JarvisCore.get_background_tasks = get_background_tasks_patch
