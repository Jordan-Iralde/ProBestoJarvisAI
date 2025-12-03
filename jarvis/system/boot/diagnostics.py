# system/boot/diagnostics.py
import time

class Diagnostics:
    def __init__(self, core):
        self.core = core
        self.results = {}

    def run(self):
        # quick health checks
        self.results['eventbus'] = self._check_eventbus()
        self.results['scheduler'] = self._check_scheduler()
        self.results['io'] = self._check_io()
        ok = all(self.results.values())
        self.core._log("DIAG", f"Diagnostics results: {self.results}")
        if not ok:
            raise RuntimeError("Diagnostics failed: " + str(self.results))

    def _check_eventbus(self):
        try:
            # lightweight smoke: start/stop cycle if not started
            eb = self.core.events
            was_started = getattr(eb, "_started", False)
            if not was_started:
                eb.start()
                time.sleep(0.01)
                eb.stop()
            return True
        except Exception:
            return False

    def _check_scheduler(self):
        try:
            sched = self.core.scheduler
            was_running = getattr(sched, "_running", None) and sched._running.is_set()
            if not was_running:
                sched.start()
                time.sleep(0.01)
                sched.stop()
            return True
        except Exception:
            return False

    def _check_io(self):
        # very basic: ensure input adapter exists
        try:
            return self.core.input is not None
        except Exception:
            return False
