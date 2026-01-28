"""
Process Monitor - PC Authority Component
Tracks running processes, detects failures, manages background tasks
"""

import psutil
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import threading

logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """Information about a process"""
    pid: int
    name: str
    status: str  # 'running', 'zombie', 'stopped', 'background'
    cpu_percent: float
    memory_percent: float
    created_time: float
    last_update: float
    failure_count: int = 0
    last_failure: Optional[float] = None
    command_line: str = ""
    parent_pid: Optional[int] = None


@dataclass
class ProcessSnapshot:
    """Process tracking state"""
    timestamp: float
    total_processes: int
    cpu_usage: float
    memory_usage: float
    active_user_processes: int
    background_processes: int
    failed_processes: int
    processes: Dict[int, ProcessInfo] = field(default_factory=dict)


class ProcessMonitor:
    """Monitor and manage system processes"""

    def __init__(self):
        self.processes: Dict[int, ProcessInfo] = {}
        self.snapshots: List[ProcessSnapshot] = []
        self.max_snapshots = 100
        self.lock = threading.Lock()
        self.enabled = True
        self.background_tasks: Dict[int, Dict] = {}  # pid -> task_config
        self.failure_threshold = 3  # Mark as failed after 3 errors
        self.failure_window = 300  # seconds - time window for counting failures

    def scan_processes(self) -> ProcessSnapshot:
        """Scan all running processes"""
        with self.lock:
            timestamp = time.time()
            current_procs = {}
            failed_count = 0

            try:
                for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent',
                                                 'memory_percent', 'create_time', 'cmdline',
                                                 'ppid']):
                    try:
                        info = ProcessInfo(
                            pid=proc.info['pid'],
                            name=proc.info['name'],
                            status=proc.info['status'],
                            cpu_percent=proc.info['cpu_percent'] or 0.0,
                            memory_percent=proc.info['memory_percent'] or 0.0,
                            created_time=proc.info['create_time'],
                            last_update=timestamp,
                            parent_pid=proc.info['ppid'],
                            command_line=' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ""
                        )

                        # Track failures
                        if proc.info['status'] in ['zombie', 'stopped', 'defunct']:
                            failed_count += 1
                            if proc.pid in self.processes:
                                info.failure_count = self.processes[proc.pid].failure_count + 1
                                info.last_failure = timestamp

                        current_procs[proc.pid] = info

                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

                # Update global process list
                self.processes = current_procs

                # Get system-wide metrics
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                memory_usage = memory.percent

                # Count background tasks
                background_count = len(self.background_tasks)

                # Create snapshot
                snapshot = ProcessSnapshot(
                    timestamp=timestamp,
                    total_processes=len(current_procs),
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    active_user_processes=len([p for p in current_procs.values() if p.status == 'running']),
                    background_processes=background_count,
                    failed_processes=failed_count,
                    processes=current_procs.copy()
                )

                # Keep snapshots history
                self.snapshots.append(snapshot)
                if len(self.snapshots) > self.max_snapshots:
                    self.snapshots.pop(0)

                return snapshot

            except Exception as e:
                logger.error(f"Error scanning processes: {e}")
                return ProcessSnapshot(
                    timestamp=timestamp,
                    total_processes=0,
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    active_user_processes=0,
                    background_processes=len(self.background_tasks),
                    failed_processes=0
                )

    def find_process_by_name(self, name: str) -> List[ProcessInfo]:
        """Find processes by name (partial match)"""
        with self.lock:
            results = []
            name_lower = name.lower()

            for proc in self.processes.values():
                if name_lower in proc.name.lower():
                    results.append(proc)

            return sorted(results, key=lambda p: p.cpu_percent, reverse=True)

    def find_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Find process by PID"""
        with self.lock:
            return self.processes.get(pid)

    def get_process_details(self, pid: int) -> Optional[Dict]:
        """Get detailed information about a process"""
        try:
            proc = psutil.Process(pid)
            info = self.processes.get(pid)

            return {
                'pid': pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_mb': proc.memory_info().rss / (1024 * 1024),
                'created_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
                'command_line': ' '.join(proc.cmdline()),
                'parent_pid': proc.ppid(),
                'num_threads': proc.num_threads(),
                'io_counters': proc.io_counters()._asdict() if hasattr(proc, 'io_counters') else None,
                'failure_count': info.failure_count if info else 0,
                'last_failure': datetime.fromtimestamp(info.last_failure).isoformat() if info and info.last_failure else None,
                'in_background': pid in self.background_tasks
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def register_background_task(self, pid: int, task_name: str, task_data: Dict) -> bool:
        """Register a process as background task (keep alive)"""
        with self.lock:
            self.background_tasks[pid] = {
                'name': task_name,
                'registered_at': time.time(),
                'data': task_data,
                'restart_count': 0,
                'last_restart': None
            }
            logger.info(f"Registered background task: {task_name} (PID: {pid})")
            return True

    def unregister_background_task(self, pid: int) -> bool:
        """Unregister a background task"""
        with self.lock:
            if pid in self.background_tasks:
                del self.background_tasks[pid]
                logger.info(f"Unregistered background task (PID: {pid})")
                return True
            return False

    def check_background_tasks(self) -> List[Tuple[int, str, bool]]:
        """Check status of background tasks
        Returns: [(pid, name, is_alive), ...]
        """
        results = []
        with self.lock:
            pids_to_remove = []

            for pid, task_config in self.background_tasks.items():
                try:
                    proc = psutil.Process(pid)
                    is_alive = proc.status() in ['running', 'sleeping']

                    if is_alive:
                        results.append((pid, task_config['name'], True))
                    else:
                        # Process is dead - should be restarted
                        results.append((pid, task_config['name'], False))
                        logger.warning(f"Background task died: {task_config['name']} (PID: {pid})")
                        task_config['restart_count'] += 1
                        task_config['last_restart'] = time.time()

                except psutil.NoSuchProcess:
                    results.append((pid, task_config['name'], False))
                    pids_to_remove.append(pid)
                    logger.warning(f"Background task process not found: {task_config['name']} (PID: {pid})")

            # Clean up dead tasks
            for pid in pids_to_remove:
                del self.background_tasks[pid]

        return results

    def get_failed_processes(self) -> List[ProcessInfo]:
        """Get processes that have failed multiple times"""
        with self.lock:
            failed = []
            current_time = time.time()

            for proc in self.processes.values():
                # Count failures in the window
                recent_failures = proc.failure_count
                if proc.last_failure and (current_time - proc.last_failure) > self.failure_window:
                    # Reset if outside window
                    recent_failures = 0

                if recent_failures >= self.failure_threshold:
                    failed.append(proc)

            return sorted(failed, key=lambda p: p.failure_count, reverse=True)

    def get_system_summary(self) -> Dict:
        """Get summary of system state"""
        snapshot = self.scan_processes()

        return {
            'timestamp': datetime.fromtimestamp(snapshot.timestamp).isoformat(),
            'total_processes': snapshot.total_processes,
            'cpu_usage_percent': snapshot.cpu_usage,
            'memory_usage_percent': snapshot.memory_usage,
            'active_processes': snapshot.active_user_processes,
            'background_tasks': snapshot.background_processes,
            'failed_processes': snapshot.failed_processes,
            'disk_usage': self._get_disk_usage(),
            'uptime_seconds': psutil.boot_time() and (time.time() - psutil.boot_time())
        }

    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage for main partitions"""
        usage = {}
        try:
            for partition in psutil.disk_partitions():
                if partition.fstype:  # Skip invalid partitions
                    du = psutil.disk_usage(partition.mountpoint)
                    usage[partition.mountpoint] = {
                        'total_gb': du.total / (1024**3),
                        'used_gb': du.used / (1024**3),
                        'free_gb': du.free / (1024**3),
                        'percent': du.percent
                    }
        except Exception as e:
            logger.warning(f"Error getting disk usage: {e}")

        return usage

    def get_top_processes(self, metric: str = 'cpu_percent', limit: int = 5) -> List[Dict]:
        """Get top processes by metric (cpu_percent, memory_percent)"""
        with self.lock:
            processes_list = list(self.processes.values())

            if metric == 'cpu_percent':
                sorted_list = sorted(processes_list, key=lambda p: p.cpu_percent, reverse=True)
            elif metric == 'memory_percent':
                sorted_list = sorted(processes_list, key=lambda p: p.memory_percent, reverse=True)
            else:
                sorted_list = sorted(processes_list, key=lambda p: p.cpu_percent, reverse=True)

            return [
                {
                    'pid': p.pid,
                    'name': p.name,
                    'cpu_percent': p.cpu_percent,
                    'memory_percent': p.memory_percent,
                    'memory_mb': (p.memory_percent / 100.0) * psutil.virtual_memory().total / (1024 * 1024),
                    'status': p.status
                }
                for p in sorted_list[:limit]
            ]

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process (gracefully or forcefully)"""
        try:
            proc = psutil.Process(pid)

            if force:
                proc.kill()
                logger.info(f"Killed process {pid} forcefully")
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                    logger.info(f"Terminated process {pid} gracefully")
                except psutil.TimeoutExpired:
                    proc.kill()
                    logger.info(f"Killed process {pid} after timeout")

            return True

        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} not found")
            return False
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False

    def suspend_process(self, pid: int) -> bool:
        """Suspend a process"""
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            logger.info(f"Suspended process {pid}")
            return True
        except Exception as e:
            logger.error(f"Error suspending process {pid}: {e}")
            return False

    def resume_process(self, pid: int) -> bool:
        """Resume a suspended process"""
        try:
            proc = psutil.Process(pid)
            proc.resume()
            logger.info(f"Resumed process {pid}")
            return True
        except Exception as e:
            logger.error(f"Error resuming process {pid}: {e}")
            return False

    def get_process_tree(self, pid: int) -> Dict:
        """Get process tree (process and children)"""
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)

            tree = {
                'process': {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(),
                    'memory_mb': proc.memory_info().rss / (1024 * 1024)
                },
                'children': []
            }

            for child in children:
                try:
                    tree['children'].append({
                        'pid': child.pid,
                        'name': child.name(),
                        'status': child.status(),
                        'cpu_percent': child.cpu_percent(),
                        'memory_mb': child.memory_info().rss / (1024 * 1024)
                    })
                except:
                    pass

            return tree

        except Exception as e:
            logger.error(f"Error getting process tree for {pid}: {e}")
            return {}

    def get_status_report(self) -> str:
        """Get human-readable status report"""
        summary = self.get_system_summary()
        failed = self.get_failed_processes()
        top_cpu = self.get_top_processes('cpu_percent', limit=3)

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║          PC AUTHORITY - PROCESS MONITOR STATUS            ║
╠═══════════════════════════════════════════════════════════╣
║ Timestamp: {summary['timestamp']}
║ Total Processes: {summary['total_processes']}
║ Active Processes: {summary['active_processes']}
║ Background Tasks: {summary['background_tasks']}
║ Failed Processes: {summary['failed_processes']}
║ CPU Usage: {summary['cpu_usage_percent']:.1f}%
║ Memory Usage: {summary['memory_usage_percent']:.1f}%
╠═══════════════════════════════════════════════════════════╣
║ TOP CPU CONSUMERS:
"""
        for i, proc in enumerate(top_cpu, 1):
            report += f"║ {i}. {proc['name']} (PID: {proc['pid']}) - {proc['cpu_percent']:.1f}%\n"

        if failed:
            report += "║\n║ FAILED PROCESSES:\n"
            for proc in failed[:3]:
                report += f"║ • {proc.name} (PID: {proc.pid}) - {proc.failure_count} failures\n"

        report += "╚═══════════════════════════════════════════════════════════╝\n"
        return report
