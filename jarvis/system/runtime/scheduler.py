# system/runtime/scheduler.py
import threading
import time
import heapq
import traceback

class Scheduler:
    def __init__(self):
        self._tasks = []
        self._lock = threading.Lock()
        self._thread = None
        self._running = threading.Event()

    def start(self):
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(target=self._loop, name="Scheduler", daemon=True)
        self._thread.start()

    def stop(self):
        if not self._running.is_set():
            return
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=2.0)

    def schedule_every(self, interval_seconds, fn, *args, **kwargs):
        run_at = time.time() + interval_seconds
        with self._lock:
            heapq.heappush(self._tasks, (run_at, interval_seconds, fn, args, kwargs))

    def _loop(self):
        while self._running.is_set():
            now = time.time()
            to_run = []
            with self._lock:
                while self._tasks and self._tasks[0][0] <= now:
                    run_at, interval, fn, args, kwargs = heapq.heappop(self._tasks)
                    to_run.append((interval, fn, args, kwargs))
                # next wait time
                next_wait = None
                if self._tasks:
                    next_wait = max(0.0, self._tasks[0][0] - now)
            for interval, fn, args, kwargs in to_run:
                try:
                    fn(*args, **kwargs)
                except Exception:
                    traceback.print_exc()
                # re-schedule
                if interval and self._running.is_set():
                    with self._lock:
                        heapq.heappush(self._tasks, (time.time() + interval, interval, fn, args, kwargs))
            time.sleep(next_wait if next_wait is not None else 0.1)
