"""
Background Task Manager - Keep tasks alive
Manages background tasks, prevents them from dying, monitors their state
"""

import threading
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    BACKGROUND = "background"


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class BackgroundTask:
    """Background task definition"""
    task_id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.QUEUED
    priority: int = 0  # Higher = more important
    max_retries: int = 3
    retry_count: int = 0
    timeout: Optional[float] = None
    result: Optional[TaskResult] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    thread: Optional[threading.Thread] = None
    memory_data: Dict = field(default_factory=dict)  # Store context/memory


class BackgroundTaskManager:
    """Manage background tasks"""

    def __init__(self, max_workers: int = 5, keep_results_count: int = 100):
        self.tasks: Dict[str, BackgroundTask] = {}
        self.results_history: List[TaskResult] = []
        self.max_workers = max_workers
        self.keep_results_count = keep_results_count
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(max_workers)
        self.enabled = True
        self.active_threads = 0
        self.completed_tasks = 0

    def submit_task(self, task_id: str, name: str, function: Callable,
                   args: tuple = (), kwargs: dict = None, priority: int = 0,
                   max_retries: int = 3, timeout: Optional[float] = None,
                   memory_data: Dict = None) -> str:
        """Submit a background task"""

        with self.lock:
            # Check if task already exists
            if task_id in self.tasks:
                logger.warning(f"Task {task_id} already exists, updating...")
                del self.tasks[task_id]

            task = BackgroundTask(
                task_id=task_id,
                name=name,
                function=function,
                args=args or (),
                kwargs=kwargs or {},
                status=TaskStatus.QUEUED,
                priority=priority,
                max_retries=max_retries,
                timeout=timeout,
                memory_data=memory_data or {}
            )

            self.tasks[task_id] = task
            logger.info(f"Task submitted: {name} ({task_id}) - Priority: {priority}")

            # Execute in background
            self._execute_task_async(task_id)

            return task_id

    def _execute_task_async(self, task_id: str):
        """Execute task in background thread"""
        task = self.tasks.get(task_id)
        if not task:
            return

        def run():
            try:
                self.semaphore.acquire()
                self.active_threads += 1

                task.status = TaskStatus.RUNNING
                task.started_at = time.time()
                logger.info(f"Task executing: {task.name} ({task_id})")

                start_time = time.time()

                # Execute with timeout
                if task.timeout:
                    import signal

                    def timeout_handler(signum, frame):
                        raise TimeoutError(f"Task timeout after {task.timeout}s")

                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(task.timeout))

                    try:
                        result = task.function(*task.args, **task.kwargs)
                        signal.alarm(0)  # Cancel alarm
                    except TimeoutError as e:
                        raise e
                else:
                    result = task.function(*task.args, **task.kwargs)

                execution_time = time.time() - start_time

                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.result = TaskResult(
                    task_id=task_id,
                    success=True,
                    output=str(result),
                    execution_time=execution_time
                )

                logger.info(f"Task completed: {task.name} ({task_id}) in {execution_time:.2f}s")
                self.completed_tasks += 1

                # Store in history
                with self.lock:
                    self.results_history.append(task.result)
                    if len(self.results_history) > self.keep_results_count:
                        self.results_history.pop(0)

            except Exception as e:
                execution_time = time.time() - (task.started_at or time.time())
                logger.error(f"Task failed: {task.name} ({task_id}): {e}")

                task.retry_count += 1

                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.QUEUED
                    logger.info(f"Retrying task: {task.name} ({task_id}) - Attempt {task.retry_count + 1}/{task.max_retries}")
                    # Retry after delay
                    time.sleep(1 * task.retry_count)
                    self._execute_task_async(task_id)
                else:
                    task.status = TaskStatus.FAILED
                    task.completed_at = time.time()
                    task.result = TaskResult(
                        task_id=task_id,
                        success=False,
                        error=str(e),
                        execution_time=execution_time
                    )
                    logger.error(f"Task permanently failed: {task.name} ({task_id})")

            finally:
                self.active_threads -= 1
                self.semaphore.release()

        thread = threading.Thread(target=run, daemon=False)
        task.thread = thread
        thread.start()

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return None

            return {
                'task_id': task_id,
                'name': task.name,
                'status': task.status.value,
                'progress': self._calculate_progress(task),
                'created_at': datetime.fromtimestamp(task.created_at).isoformat(),
                'started_at': datetime.fromtimestamp(task.started_at).isoformat() if task.started_at else None,
                'completed_at': datetime.fromtimestamp(task.completed_at).isoformat() if task.completed_at else None,
                'retry_count': task.retry_count,
                'max_retries': task.max_retries,
                'result': task.result.__dict__ if task.result else None,
                'active': task.status in [TaskStatus.RUNNING, TaskStatus.QUEUED]
            }

    def _calculate_progress(self, task: BackgroundTask) -> float:
        """Calculate task progress (estimated)"""
        if task.status == TaskStatus.COMPLETED:
            return 100.0
        elif task.status == TaskStatus.FAILED:
            return 0.0
        elif task.status == TaskStatus.RUNNING:
            # Estimate based on execution time
            if task.started_at and task.timeout:
                elapsed = time.time() - task.started_at
                progress = (elapsed / task.timeout) * 100
                return min(progress, 99.0)
            return 50.0
        elif task.status == TaskStatus.QUEUED:
            return 10.0
        else:
            return 0.0

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """Wait for task to complete"""
        start_time = time.time()

        while True:
            with self.lock:
                task = self.tasks.get(task_id)
                if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    return task.result

            if timeout:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.warning(f"Timeout waiting for task {task_id}")
                    return None

            time.sleep(0.1)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return False

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return False

            task.status = TaskStatus.CANCELLED
            logger.info(f"Task cancelled: {task.name} ({task_id})")
            return True

    def pause_task(self, task_id: str) -> bool:
        """Pause a task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.RUNNING:
                return False

            task.status = TaskStatus.PAUSED
            logger.info(f"Task paused: {task.name} ({task_id})")
            return True

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.PAUSED:
                return False

            task.status = TaskStatus.RUNNING
            logger.info(f"Task resumed: {task.name} ({task_id})")
            return True

    def get_all_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Dict]:
        """Get all tasks"""
        with self.lock:
            tasks = []
            for task_id, task in self.tasks.items():
                if status_filter and task.status != status_filter:
                    continue

                tasks.append({
                    'task_id': task_id,
                    'name': task.name,
                    'status': task.status.value,
                    'priority': task.priority,
                    'created_at': datetime.fromtimestamp(task.created_at).isoformat(),
                    'active': task.status in [TaskStatus.RUNNING, TaskStatus.QUEUED]
                })

            return sorted(tasks, key=lambda t: t['priority'], reverse=True)

    def get_active_tasks(self) -> List[Dict]:
        """Get currently active tasks"""
        return self.get_all_tasks(status_filter=TaskStatus.RUNNING)

    def get_queued_tasks(self) -> List[Dict]:
        """Get queued tasks"""
        return self.get_all_tasks(status_filter=TaskStatus.QUEUED)

    def get_results_history(self, limit: int = 10) -> List[Dict]:
        """Get results history"""
        with self.lock:
            return [
                {
                    'task_id': r.task_id,
                    'success': r.success,
                    'output': r.output[:200] if r.output else None,
                    'error': r.error[:200] if r.error else None,
                    'execution_time': r.execution_time,
                    'created_at': datetime.fromtimestamp(r.created_at).isoformat()
                }
                for r in sorted(self.results_history, key=lambda r: r.created_at, reverse=True)[:limit]
            ]

    def get_statistics(self) -> Dict:
        """Get task manager statistics"""
        with self.lock:
            total_tasks = len(self.tasks)
            running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            queued_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.QUEUED)
            completed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)

            return {
                'total_tasks': total_tasks,
                'active_tasks': running_tasks,
                'queued_tasks': queued_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'completed_count': self.completed_tasks,
                'active_threads': self.active_threads,
                'max_workers': self.max_workers,
                'results_history_size': len(self.results_history)
            }

    def get_memory_context(self, task_id: str) -> Optional[Dict]:
        """Get memory context for a task (for understanding user intent)"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return task.memory_data
            return None

    def update_memory_context(self, task_id: str, context: Dict) -> bool:
        """Update memory context for a task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                task.memory_data.update(context)
                return True
            return False

    def get_status_report(self) -> str:
        """Get human-readable status report"""
        stats = self.get_statistics()
        active = self.get_active_tasks()

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║        BACKGROUND TASK MANAGER - STATUS REPORT            ║
╠═══════════════════════════════════════════════════════════╣
║ Total Tasks: {stats['total_tasks']}
║ Active Tasks: {stats['active_tasks']} | Queued: {stats['queued_tasks']}
║ Completed: {stats['completed_tasks']} | Failed: {stats['failed_tasks']}
║ Active Threads: {stats['active_threads']}/{stats['max_workers']}
║ Total Completed: {stats['completed_count']}
╠═══════════════════════════════════════════════════════════╣
"""
        if active:
            report += "║ ACTIVE TASKS:\n"
            for task in active[:5]:
                status_str = "●" if task['active'] else "○"
                report += f"║ {status_str} {task['name']} ({task['task_id']}) - {task['status']}\n"
        else:
            report += "║ No active tasks\n"

        report += "╚═══════════════════════════════════════════════════════════╝\n"
        return report
