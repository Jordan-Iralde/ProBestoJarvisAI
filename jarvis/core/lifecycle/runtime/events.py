# core/lifecycle/runtime/events.py
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


class EventExecutor:
    def __init__(self, workers=4):
        self.queue = Queue()
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self._thread = None
        self._running = threading.Event()

    def start(self):
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(target=self._loop, name="EventExecutor", daemon=True)
        self._thread.start()

    def stop(self, wait=True):
        if not self._running.is_set():
            return
        self._running.clear()
        # push sentinel to unblock queue.get
        self.queue.put(None)
        if wait and self._thread:
            self._thread.join(timeout=2.0)
        self.pool.shutdown(wait=wait)

    def push(self, event):
        self.queue.put(event)

    def _loop(self):
        while self._running.is_set():
            event = self.queue.get()
            if event is None:
                # sentinel to stop
                continue
            handlers = event.get("handlers", [])
            for h in handlers:
                self.pool.submit(self._safe_run, h, event)

    def _safe_run(self, handler, event):
        try:
            handler(event)
        except Exception as e:
            print(f"[EventExecutor] handler error: {e}")


class EventBus:
    def __init__(self, workers=4):
        self.subscribers = {}
        self.lock = threading.RLock()
        self.executor = EventExecutor(workers=workers)
        self._started = False

    def start(self):
        with self.lock:
            if self._started:
                return
            self.executor.start()
            self._started = True

    def stop(self):
        with self.lock:
            if not self._started:
                return
            self.executor.stop(wait=True)
            self._started = False

    def subscribe(self, event_type, handler):
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        with self.lock:
            handlers = self.subscribers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

    def emit(self, event_type, data=None):
        with self.lock:
            handlers = list(self.subscribers.get(event_type, []))
        self.executor.push({
            "type": event_type,
            "data": data,
            "handlers": handlers
        })
