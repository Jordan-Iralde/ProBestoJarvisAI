# system/core.py
import time
import traceback

from system.runtime.state import RuntimeState
from system.runtime.events import EventBus
from system.runtime.scheduler import Scheduler
from system.boot.initializer import Initializer
from system.boot.diagnostics import Diagnostics
from system.boot.loader import ModuleLoader

from interface.text.input_adapter import CLIInput
from brain.nlu.pipeline import NLUPipeline
from brain.nlu.parser import IntentParser
# dispatcher legacy (event-based)

# NEW: Skill dispatcher puro
from actions.dispatcher import SkillDispatcher

# skills
from actions.skills.open_app import OpenAppSkill
from actions.skills.get_time import GetTimeSkill
from actions.skills.system_status import SystemStatusSkill
from actions.skills.create_note import CreateNoteSkill
from actions.skills.search_file import SearchFileSkill


class JarvisCore:
    def __init__(self, config):
        self.config = config
        self.state = RuntimeState()

        # runtime
        self.events = EventBus(workers=config.get("workers", 4))
        self.scheduler = Scheduler()
        self.modules_loader = ModuleLoader(self)
        # io & brain
        self.input = CLIInput(self.events)
        self.nlu = NLUPipeline()

        # dispatcher original (solo eventos)

        # dispatcher nuevo de skills
        self.skill_dispatcher = SkillDispatcher()

        # registrar skills
        self._register_skills()

        # pipeline NLU usando el registry real
        self.nlu = NLUPipeline(
            skills_registry=self.skill_dispatcher.skills,
            debug=self.config.get("debug_nlu", False)
    )

        self.events.subscribe("nlu.intent", self._handle_skill_intent)

        self._initializer = Initializer(self)
        self._diagnostics = Diagnostics(self)

    def _register_skills(self):
        self.skill_dispatcher.register("open_app", OpenAppSkill)
        self.skill_dispatcher.register("get_time", GetTimeSkill)
        self.skill_dispatcher.register("system_status", SystemStatusSkill)
        self.skill_dispatcher.register("create_note", CreateNoteSkill)
        self.skill_dispatcher.register("search_file", SearchFileSkill)

    # NUEVO: handler de intents → skills
    def _handle_skill_intent(self, event):
        try:
            payload = event.get("data", {})
            print("[DEBUG_INTENT]", payload)

            intent = payload.get("intent")
            entities = payload.get("entities", {})

            result = self.skill_dispatcher.dispatch(intent, entities, self.state)
            print(f"[SKILL] {intent} → {result}")

        except Exception as e:
            print(f"[SKILL_ERROR] {e}")
            traceback.print_exc()


    def boot(self):
        try:
            self.state.set("BOOTING")
            self._log("BOOT", "Starting boot sequence")

            self.events.start()
            self.scheduler.start()
            self._initializer.run()
            self.modules_loader.load_all()
            self._diagnostics.run()

            self.state.set("READY")
            self._log("BOOT", "Boot completed - READY")
        except Exception as e:
            self._log_error("BOOT_FAILED", e)
            self.state.set("DEAD")
            raise

    def run(self):
        if not self.state.wait_ready(timeout=5.0):
            raise RuntimeError("Core not ready to run")
        self.state.set("RUNNING")
        self._log("SYSTEM", "Loop iniciado.")
        try:
            while self.state.is_running():
                try:
                    self.input.poll()
                    time.sleep(0.01)
                except Exception as e:
                    self._log_error("CORE_LOOP_CRASH", e)
        finally:
            self.stop()

    def stop(self):
        cur = self.state.get()
        if cur in ("STOPPING", "DEAD"):
            return
        self._log("SYSTEM", "Shutting down...")
        self.state.set("STOPPING")
        try:
            try: self.scheduler.stop()
            except Exception as e: self._log_error("SCHED_STOP_ERR", e)

            try: self.events.stop()
            except Exception as e: self._log_error("EVENTS_STOP_ERR", e)

            try: self.modules_loader.stop_all()
            except Exception as e: self._log_error("MODULES_STOP_ERR", e)

            try:
                stop_fn = getattr(self.input, "stop", None)
                if callable(stop_fn):
                    stop_fn()
            except Exception as e:
                self._log_error("INPUT_STOP_ERR", e)

        finally:
            self.state.set("DEAD")
            self._log("SYSTEM", "Shutdown complete.")

    def _log(self, level, msg):
        print(f"[{level}] {msg}")

    def _log_error(self, code, exc):
        print(f"[ERROR] {code}: {exc}")
        traceback.print_exc()