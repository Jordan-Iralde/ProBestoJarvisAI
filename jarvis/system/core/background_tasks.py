# system/core/background_tasks.py
"""
Background Task Manager - Execute tasks asynchronously
For internet searches, parallel skill attempts, etc.
"""

import threading
import time
from typing import Callable, Dict, List, Optional
from datetime import datetime
import queue


class BackgroundTask:
    """Represents a background task"""
    
    def __init__(self, task_id: str, name: str, function: Callable, args=None, kwargs=None, priority=0):
        self.task_id = task_id
        self.name = name
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority  # Higher = more important
        
        self.status = 'pending'  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.duration_ms = 0
    
    def execute(self):
        """Execute the task"""
        try:
            self.status = 'running'
            self.started_at = datetime.now()
            
            self.result = self.function(*self.args, **self.kwargs)
            self.status = 'completed'
            
        except Exception as e:
            self.error = str(e)
            self.status = 'failed'
        
        finally:
            self.completed_at = datetime.now()
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
    
    def to_dict(self) -> Dict:
        """Convert to dict"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'status': self.status,
            'result': str(self.result)[:100] if self.result else None,
            'error': self.error,
            'duration_ms': self.duration_ms,
            'priority': self.priority
        }


class BackgroundTaskManager:
    """
    Manages background task execution
    Useful for:
    - Internet searches
    - Parallel skill attempts
    - Slow operations
    """
    
    def __init__(self, max_workers: int = 4, logger=None):
        self.max_workers = max_workers
        self.logger = logger
        self.task_queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: List[BackgroundTask] = []
        self.workers = []
        self.running = False
    
    def _log(self, msg: str):
        """Log message using logger or print"""
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[BACKGROUND] {msg}")
    
    def start(self):
        """Start worker threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        self._log(f"Started {self.max_workers} workers")
    
    def stop(self):
        """Stop all workers"""
        self.running = False
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=1.0)
        self._log("All workers stopped")
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while self.running:
            try:
                # Get task from queue (blocking with timeout)
                priority, task = self.task_queue.get(timeout=1.0)
                
                if task is None:  # Shutdown signal
                    break
                
                self.active_tasks[task.task_id] = task
                task.execute()
                self.completed_tasks.append(task)
                del self.active_tasks[task.task_id]
                
            except queue.Empty:
                continue
            except Exception as e:
                self._log(f"Worker error: {e}")
    
    def submit(self, name: str, function: Callable, args=None, 
               kwargs=None, priority: int = 0, task_id: str = None) -> str:
        """
        Submit a task for background execution
        Returns: task_id (str)
        """
        task_id = task_id or f"task_{int(time.time() * 1000)}"
        task = BackgroundTask(task_id, name, function, args, kwargs, priority)
        
        # Add to queue (negative priority so higher = executed sooner)
        self.task_queue.put((-priority, task))
        self._log(f"Task queued: {name} (id={task_id})")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get task by ID"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task
        
        return None
    
    def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> Optional[BackgroundTask]:
        """
        Wait for task to complete
        Returns: task or None if timeout
        """
        start = time.time()
        timeout_s = timeout_ms / 1000.0
        
        while time.time() - start < timeout_s:
            task = self.get_task(task_id)
            
            if task and task.status in ['completed', 'failed']:
                return task
            
            time.sleep(0.1)
        
        return None
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        return [task.to_dict() for task in self.active_tasks.values()]
    
    def get_completed_tasks(self, limit: int = 10) -> List[Dict]:
        """Get recently completed tasks"""
        return [task.to_dict() for task in self.completed_tasks[-limit:]]
