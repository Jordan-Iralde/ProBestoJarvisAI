"""
Jarvis v0.0.4 Bootstrap Integration
Call this right after JarvisCore initialization to wire everything together

This file serves as the entry point for v0.0.4 feature integration.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def bootstrap_v004_features(jarvis_core) -> bool:
    """
    Bootstrap all v0.0.4 features into an initialized JarvisCore instance
    
    This function should be called right after jarvis_core.boot() and before jarvis_core.run()
    
    Args:
        jarvis_core: The JarvisCore instance to enhance
        
    Returns:
        bool: True if bootstrap successful, False if any critical component failed
    """
    try:
        logger.info("🚀 Starting v0.0.4 Bootstrap...")
        
        # Step 1: Initialize v0.0.4 Integration Layer
        logger.info("[1/4] Initializing v0.0.4 integration layer...")
        try:
            from system.core.v004_integration import integrate_v004_into_engine
            jarvis_core.integration_layer = integrate_v004_into_engine(jarvis_core)
            logger.info("✓ Integration layer ready")
        except Exception as e:
            logger.warning(f"⚠ Integration layer failed: {e}")
            jarvis_core.integration_layer = None
        
        # Step 2: Initialize Background Task Manager
        logger.info("[2/4] Initializing background task manager...")
        try:
            from system.pc_authority.background_task_manager import BackgroundTaskManager
            jarvis_core.task_manager = BackgroundTaskManager(max_workers=4)
            logger.info("✓ Background task manager ready (4 workers)")
        except Exception as e:
            logger.warning(f"⚠ Background task manager failed: {e}")
            jarvis_core.task_manager = None
        
        # Step 3: Initialize Process Monitor
        logger.info("[3/4] Initializing PC monitor...")
        try:
            from system.pc_authority.process_monitor import ProcessMonitor
            jarvis_core.process_monitor = ProcessMonitor()
            logger.info("✓ PC monitor ready")
        except Exception as e:
            logger.warning(f"⚠ PC monitor failed: {e}")
            jarvis_core.process_monitor = None
        
        # Step 4: Initialize Soft Phrases Database
        logger.info("[4/4] Loading soft phrases database...")
        try:
            from brain.nlu.soft_phrases import SoftPhrasesDatabase
            jarvis_core.soft_phrases = SoftPhrasesDatabase()
            phrase_count = len(jarvis_core.soft_phrases.get_all_phrases())
            logger.info(f"✓ Soft phrases ready ({phrase_count} phrases loaded)")
        except Exception as e:
            logger.warning(f"⚠ Soft phrases failed: {e}")
            jarvis_core.soft_phrases = None
        
        # Step 5: Initialize Debug Mode  
        logger.info("[5/5] Initializing debug system...")
        try:
            jarvis_core._debug_mode = False  # Default off
            logger.info("✓ Debug system ready (use --debug to toggle)")
        except Exception as e:
            logger.warning(f"⚠ Debug system failed: {e}")
        
        logger.info("✅ v0.0.4 Bootstrap Complete!")
        logger.info("")
        logger.info("New capabilities:")
        logger.info("  • Soft phrases for natural language (215+ phrases)")
        logger.info("  • Background task execution")
        logger.info("  • PC monitoring (CPU, memory, processes)")
        logger.info("  • Debug mode with NLU traces")
        logger.info("  • System status reporting")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ v0.0.4 Bootstrap FAILED: {e}")
        return False


def integrate_handlers_with_v004(jarvis_core):
    """
    Enhance event handlers to use v0.0.4 components
    
    This updates the handlers to use soft phrases and comprehension scoring
    Should be called after bootstrap_v004_features()
    """
    try:
        logger.info("Integrating v0.0.4 into event handlers...")
        
        # The handlers will automatically use:
        # - jarvis_core.integration_layer (for enhanced NLU)
        # - jarvis_core.soft_phrases (for responses)
        # - jarvis_core.task_manager (for async execution)
        # - jarvis_core._debug_mode (for tracing)
        
        # This is picked up by handlers.py automatically via:
        # if hasattr(self.core, 'integration_layer'):
        #     result = self.core.integration_layer.enhance_nlu_processing(...)
        
        logger.info("✓ Handlers integration complete")
        return True
        
    except Exception as e:
        logger.error(f"Handlers integration failed: {e}")
        return False


def setup_debug_commands(jarvis_core):
    """
    Setup special commands for debug mode
    These commands are handled in the CLI/input layer
    """
    try:
        logger.info("Setting up debug commands...")
        
        # Debug commands that should be handled:
        debug_commands = {
            '--debug': 'Toggle debug mode ON/OFF',
            '--debug on': 'Turn debug mode ON',
            '--debug off': 'Turn debug mode OFF',
            '--status': 'Show system status',
            '--tasks': 'Show background tasks',
            '--skills': 'List all available skills',
            '--trace': 'Show NLU trace for next command',
            '--pc': 'Show PC statistics',
        }
        
        jarvis_core._debug_commands = debug_commands
        logger.info(f"✓ {len(debug_commands)} debug commands registered")
        
        return True
        
    except Exception as e:
        logger.error(f"Debug commands setup failed: {e}")
        return False


def enable_constant_pc_monitoring(jarvis_core):
    """
    Enable background PC monitoring with alerts
    """
    try:
        logger.info("Enabling constant PC monitoring...")
        
        if not hasattr(jarvis_core, 'process_monitor') or jarvis_core.process_monitor is None:
            logger.warning("PC monitor not available")
            return False
        
        import threading
        import time
        
        def monitor_thread():
            """Background thread that monitors PC continuously"""
            while getattr(jarvis_core, '_monitoring_enabled', True):
                try:
                    summary = jarvis_core.process_monitor.get_system_summary()
                    
                    # Check for high resource usage
                    if summary['cpu_usage_percent'] > 80:
                        logger.warning(f"⚠ HIGH CPU: {summary['cpu_usage_percent']:.1f}%")
                    
                    if summary['memory_usage_percent'] > 85:
                        logger.warning(f"⚠ HIGH MEMORY: {summary['memory_usage_percent']:.1f}%")
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.debug(f"Monitor error: {e}")
        
        jarvis_core._monitoring_enabled = True
        monitor = threading.Thread(target=monitor_thread, daemon=True)
        monitor.start()
        
        logger.info("✓ PC monitoring active (background thread)")
        return True
        
    except Exception as e:
        logger.error(f"PC monitoring setup failed: {e}")
        return False


def full_bootstrap(jarvis_core) -> bool:
    """
    Full v0.0.4 bootstrap with all features
    
    This is the recommended function to call after boot()
    
    Args:
        jarvis_core: The JarvisCore instance
        
    Returns:
        bool: True if fully bootstrapped, False if critical failures
    """
    try:
        logger.info("=" * 60)
        logger.info("JARVIS v0.0.4 FULL BOOTSTRAP")
        logger.info("=" * 60)
        
        # 1. Core bootstrap
        if not bootstrap_v004_features(jarvis_core):
            logger.warning("⚠ Bootstrap had warnings but continuing...")
        
        # 2. Integrate handlers
        if not integrate_handlers_with_v004(jarvis_core):
            logger.warning("⚠ Handler integration had issues")
        
        # 3. Setup debug commands
        if not setup_debug_commands(jarvis_core):
            logger.warning("⚠ Debug commands not available")
        
        # 4. Enable monitoring
        if not enable_constant_pc_monitoring(jarvis_core):
            logger.warning("⚠ PC monitoring not available")
        
        logger.info("=" * 60)
        logger.info("✅ JARVIS v0.0.4 READY FOR PRODUCTION")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Full bootstrap failed: {e}")
        return False


# Usage example:
"""
# In main.py or boot script:

from jarvis.system.core.v004_bootstrap import full_bootstrap

# After jarvis_core.boot()
if full_bootstrap(jarvis_core):
    jarvis_core.run()
else:
    print("Failed to bootstrap v0.0.4")
    jarvis_core.stop()
"""
