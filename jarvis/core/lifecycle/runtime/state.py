# core/lifecycle/runtime/state.py
import threading
import time


class RuntimeState:
    STATES = ("INIT", "BOOTING", "READY", "RUNNING", "STOPPING", "DEAD")

    def __init__(self):
        self._state = "INIT"
        self._cond = threading.Condition()

    def set(self, value):
        if value not in self.STATES:
            raise ValueError(f"invalid state: {value}")
        with self._cond:
            self._state = value
            self._cond.notify_all()

    def get(self):
        with self._cond:
            return self._state

    def is_(self, value):
        return self.get() == value

    def wait_for(self, predicate, timeout=None):
        end = None if timeout is None else time.time() + timeout
        with self._cond:
            while not predicate():
                remaining = None if end is None else end - time.time()
                if remaining is not None and remaining <= 0:
                    return False
                self._cond.wait(timeout=remaining)
            return True

    # convenience
    def wait_ready(self, timeout=10.0):
        return self.wait_for(lambda: self._state == "READY", timeout=timeout)

    def is_running(self):
        return self.get() == "RUNNING"
