# system/core/boot_manager.py
"""
Boot Manager for JarvisAI Core
Handles system initialization and startup sequence
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import JarvisCore


class BootManager:
    """
    Manages the boot sequence and initialization of JarvisAI components
    """

    def __init__(self, core: 'JarvisCore'):
        self.core = core

    def boot(self) -> bool:
        """
        Execute the complete boot sequence

        Returns:
            bool: True if boot successful, False otherwise
        """
        try:
            self.core.state.set("BOOTING")
            self.core.logger.logger.info("🚀 Starting boot sequence")

            # Initialize runtime components
            if not self._init_runtime_components():
                return False

            # Initialize voice pipeline
            if not self._init_voice_pipeline():
                return False

            # Run diagnostics
            if not self._run_diagnostics():
                return False

            # Create initial session
            if not self._create_initial_session():
                return False

            # Initialize legacy components (deprecated)
            self._init_legacy_components()

            self.core.state.set("READY")
            self.core.logger.logger.info("✓ Boot completed - READY")

            # Show suggestions if available
            self._show_suggestions()

            return True

        except Exception as e:
            self.core.logger.log_error("BOOT_FAILED", str(e))
            self.core.logger.logger.critical(f"Boot failed: {e}")
            self.core.state.set("DEAD")
            return False

    def _init_runtime_components(self) -> bool:
        """Initialize core runtime components"""
        try:
            self.core.logger.logger.info("Starting EventBus...")
            self.core.events.start()

            self.core.logger.logger.info("Starting Scheduler...")
            self.core.scheduler.start()

            # Scheduler: Collect metrics every 5 minutes
            if self.core.config.get("data_collection", False):
                self.core.scheduler.schedule_every(300, self.core.data_collector.collect_system_snapshot)

            self.core.logger.logger.info("Running initializers...")
            self.core._initializer.run()

            self.core.logger.logger.info("Loading modules...")
            self.core.modules_loader.load_all()

            return True
        except Exception as e:
            self.core.logger.logger.error(f"Failed to initialize runtime components: {e}")
            return False

    def _init_voice_pipeline(self) -> bool:
        """Initialize voice IO pipeline"""
        try:
            self.core.logger.logger.info("Initializing Voice IO Pipeline...")
            self.core.voice_pipeline.set_eventbus(self.core.events)

            if self.core.voice_pipeline.start():
                self.core.logger.logger.info("[VOICE] Voice IO Pipeline started")
                return True
            else:
                self.core.logger.logger.warning("[VOICE] Voice IO Pipeline not available, using CLI fallback")
                return True  # Not a fatal error
        except Exception as e:
            self.core.logger.logger.error(f"Failed to initialize voice pipeline: {e}")
            return False

    def _run_diagnostics(self) -> bool:
        """Run system diagnostics"""
        try:
            self.core.logger.logger.info("Running diagnostics...")
            self.core._diagnostics.run()
            return True
        except Exception as e:
            self.core.logger.logger.error(f"Diagnostics failed: {e}")
            return False

    def _create_initial_session(self) -> bool:
        """Create the initial user session"""
        try:
            self.core.logger.logger.info("Creating initial session...")
            self.core.current_session_id = self.core.session_manager.create_session()
            self.core.cli.set_session(self.core.current_session_id)
            self.core.logger.logger.info(f"[SESSION] Created session: {self.core.current_session_id}")
            return True
        except Exception as e:
            self.core.logger.logger.error(f"Failed to create initial session: {e}")
            return False

    def _init_legacy_components(self):
        """Initialize legacy components (deprecated)"""
        try:
            # Legacy STT (deprecated - will be removed)
            if self.core.stt.start(self.core.events):
                self.core.logger.logger.info("[STT] Legacy STT started (wake word: jarvis)")
            else:
                self.core.logger.logger.warning("[STT] Legacy STT not available")
        except Exception as e:
            self.core.logger.logger.warning(f"Legacy STT initialization failed: {e}")

    def _show_suggestions(self):
        """Show usage suggestions if available"""
        try:
            suggestions = self.core.data_collector.get_suggestions()
            if suggestions:
                print("\n💡 Sugerencias basadas en tu uso:")
                for s in suggestions:
                    print(f"   {s}")
                print()
        except Exception as e:
            self.core.logger.logger.warning(f"Failed to show suggestions: {e}")