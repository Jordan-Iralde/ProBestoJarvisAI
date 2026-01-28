"""
System Authority - PC Control
Control total sobre la PC: procesos, teclado, mouse, recursos del sistema
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import psutil
import os
import subprocess

logger = logging.getLogger(__name__)

# Try to import keyboard and mouse libraries
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("keyboard library not available - keyboard tracking disabled")

try:
    import mouse
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False
    logger.warning("mouse library not available - mouse tracking disabled")


@dataclass
class KeyboardEvent:
    """Keyboard event record"""
    timestamp: float
    key: str
    event_type: str  # 'press', 'release', 'type'
    modifiers: List[str] = None  # ['shift', 'ctrl', 'alt']


@dataclass
class MouseEvent:
    """Mouse event record"""
    timestamp: float
    x: int
    y: int
    event_type: str  # 'move', 'click', 'scroll'
    button: Optional[str] = None  # 'left', 'right', 'middle'
    delta: Optional[int] = None  # for scroll


@dataclass
class SystemResourceSnapshot:
    """System resource usage snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_mb_free: float
    cpu_count: int
    cpu_frequency_mhz: float


class KeyboardTracker:
    """Track keyboard events"""

    def __init__(self, max_events: int = 100):
        self.events: List[KeyboardEvent] = []
        self.max_events = max_events
        self.enabled = KEYBOARD_AVAILABLE
        self.listener = None
        self.lock = threading.Lock()
        self.tracking = False

    def start_tracking(self):
        """Start keyboard tracking"""
        if not self.enabled:
            logger.warning("Keyboard tracking not available")
            return

        try:
            self.listener = keyboard.on_press(self._on_key_event)
            self.tracking = True
            logger.info("Keyboard tracking started")
        except Exception as e:
            logger.error(f"Error starting keyboard tracking: {e}")
            self.enabled = False

    def stop_tracking(self):
        """Stop keyboard tracking"""
        if self.listener:
            try:
                keyboard.remove_hotkey(self.listener)
                self.listener = None
                self.tracking = False
                logger.info("Keyboard tracking stopped")
            except Exception as e:
                logger.error(f"Error stopping keyboard tracking: {e}")
        self.tracking = False

    def _on_key_event(self, event):
        """Handle keyboard event"""
        with self.lock:
            event_obj = KeyboardEvent(
                timestamp=time.time(),
                key=event.name,
                event_type='press' if event.event_type == keyboard.KEY_DOWN else 'release',
                modifiers=self._get_modifiers()
            )

            self.events.append(event_obj)

            # Keep history limited
            if len(self.events) > self.max_events:
                self.events.pop(0)

    def _get_modifiers(self) -> List[str]:
        """Get currently pressed modifiers"""
        try:
            modifiers = []
            if keyboard.is_pressed('shift'):
                modifiers.append('shift')
            if keyboard.is_pressed('ctrl'):
                modifiers.append('ctrl')
            if keyboard.is_pressed('alt'):
                modifiers.append('alt')
            return modifiers
        except:
            return []

    def get_recent_keys(self, count: int = 10) -> List[Dict]:
        """Get recent key presses"""
        with self.lock:
            return [
                {
                    'timestamp': e.timestamp,
                    'key': e.key,
                    'modifiers': e.modifiers
                }
                for e in self.events[-count:]
            ]

    def get_typed_text(self, last_seconds: float = 5.0) -> str:
        """Try to reconstruct typed text from recent key events"""
        with self.lock:
            current_time = time.time()
            recent_events = [e for e in self.events 
                           if (current_time - e.timestamp) <= last_seconds
                           and e.event_type == 'press']

            # Simple reconstruction (alphanumeric and space)
            text = ""
            for event in recent_events:
                if len(event.key) == 1 and event.key.isalnum():
                    text += event.key
                elif event.key == 'space':
                    text += " "
                elif event.key in ['enter', 'return']:
                    text += "\n"

            return text


class MouseTracker:
    """Track mouse events"""

    def __init__(self, max_events: int = 100):
        self.events: List[MouseEvent] = []
        self.max_events = max_events
        self.enabled = MOUSE_AVAILABLE
        self.tracking = False
        self.last_position: Tuple[int, int] = (0, 0)
        self.lock = threading.Lock()

    def start_tracking(self):
        """Start mouse tracking"""
        if not self.enabled:
            logger.warning("Mouse tracking not available")
            return

        self.tracking = True
        self.listener = threading.Thread(target=self._track_loop, daemon=True)
        self.listener.start()
        logger.info("Mouse tracking started")

    def stop_tracking(self):
        """Stop mouse tracking"""
        self.tracking = False
        logger.info("Mouse tracking stopped")

    def _track_loop(self):
        """Background thread for mouse tracking"""
        try:
            mouse.on_move(self._on_mouse_move)
            mouse.on_click(self._on_mouse_click)
            mouse.on_scroll(self._on_mouse_scroll)
        except Exception as e:
            logger.error(f"Error in mouse tracking: {e}")
            self.enabled = False

    def _on_mouse_move(self, event):
        """Handle mouse move"""
        x, y = event.x, event.y

        # Only record if position changed significantly
        if (abs(x - self.last_position[0]) > 10 or 
            abs(y - self.last_position[1]) > 10):

            with self.lock:
                event_obj = MouseEvent(
                    timestamp=time.time(),
                    x=x,
                    y=y,
                    event_type='move'
                )
                self.events.append(event_obj)
                self.last_position = (x, y)

                if len(self.events) > self.max_events:
                    self.events.pop(0)

    def _on_mouse_click(self, event):
        """Handle mouse click"""
        with self.lock:
            button_map = {1: 'left', 2: 'middle', 3: 'right'}
            event_obj = MouseEvent(
                timestamp=time.time(),
                x=event.x,
                y=event.y,
                event_type='click',
                button=button_map.get(event.button, str(event.button))
            )
            self.events.append(event_obj)

            if len(self.events) > self.max_events:
                self.events.pop(0)

    def _on_mouse_scroll(self, event):
        """Handle mouse scroll"""
        with self.lock:
            event_obj = MouseEvent(
                timestamp=time.time(),
                x=event.x,
                y=event.y,
                event_type='scroll',
                delta=event.delta
            )
            self.events.append(event_obj)

            if len(self.events) > self.max_events:
                self.events.pop(0)

    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        try:
            return mouse.get_position()
        except:
            return self.last_position

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to position"""
        try:
            mouse.move(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return False

    def click(self, x: int = None, y: int = None, button: str = 'left') -> bool:
        """Click at position"""
        try:
            if x is not None and y is not None:
                mouse.click(button, x, y)
            else:
                mouse.click(button)
            return True
        except Exception as e:
            logger.error(f"Error clicking: {e}")
            return False

    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """Get recent mouse events"""
        with self.lock:
            return [
                {
                    'timestamp': e.timestamp,
                    'position': (e.x, e.y),
                    'event_type': e.event_type,
                    'button': e.button
                }
                for e in self.events[-count:]
            ]


class SystemAuthorityController:
    """Central system authority control"""

    def __init__(self):
        self.keyboard = KeyboardTracker()
        self.mouse = MouseTracker()
        self.resources_snapshots: List[SystemResourceSnapshot] = []
        self.max_snapshots = 100
        self.enabled = True
        self.lock = threading.Lock()

    def start(self):
        """Start all tracking"""
        self.keyboard.start_tracking()
        self.mouse.start_tracking()
        logger.info("System authority control started")

    def stop(self):
        """Stop all tracking"""
        self.keyboard.stop_tracking()
        self.mouse.stop_tracking()
        logger.info("System authority control stopped")

    def get_resource_snapshot(self) -> SystemResourceSnapshot:
        """Get current system resource snapshot"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_freq = psutil.cpu_freq()

            snapshot = SystemResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_percent=disk.percent,
                disk_mb_free=disk.free / (1024 * 1024),
                cpu_count=psutil.cpu_count(),
                cpu_frequency_mhz=cpu_freq.current if cpu_freq else 0.0
            )

            with self.lock:
                self.resources_snapshots.append(snapshot)
                if len(self.resources_snapshots) > self.max_snapshots:
                    self.resources_snapshots.pop(0)

            return snapshot

        except Exception as e:
            logger.error(f"Error getting resource snapshot: {e}")
            return None

    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        snapshot = self.get_resource_snapshot()
        if not snapshot:
            return {}

        return {
            'cpu': {
                'percent': snapshot.cpu_percent,
                'count': snapshot.cpu_count,
                'frequency_mhz': snapshot.cpu_frequency_mhz
            },
            'memory': {
                'used_mb': snapshot.memory_mb,
                'available_mb': snapshot.memory_available_mb,
                'percent': snapshot.memory_percent
            },
            'disk': {
                'free_mb': snapshot.disk_mb_free,
                'percent': snapshot.disk_percent
            },
            'keyboard_available': self.keyboard.enabled,
            'mouse_available': self.mouse.enabled,
            'tracking_active': self.keyboard.tracking or self.mouse.tracking
        }

    def get_current_activity(self) -> Dict:
        """Get current user activity"""
        return {
            'mouse_position': self.mouse.get_current_position(),
            'recent_keys': self.keyboard.get_recent_keys(5),
            'recent_mouse_events': self.mouse.get_recent_events(5),
            'recent_typed_text': self.keyboard.get_typed_text(3.0)
        }

    def execute_command(self, command: str, shell: bool = True) -> Tuple[bool, str]:
        """Execute a system command"""
        try:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=5)
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)

    def get_authority_report(self) -> str:
        """Get system authority status report"""
        info = self.get_system_info()
        activity = self.get_current_activity()

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║              SYSTEM AUTHORITY - CONTROL REPORT             ║
╠═══════════════════════════════════════════════════════════╣
║ RESOURCES:
║ ├─ CPU: {info.get('cpu', {}).get('percent', 0):.1f}% ({info.get('cpu', {}).get('count', 0)} cores)
║ ├─ Memory: {info.get('memory', {}).get('percent', 0):.1f}% ({info.get('memory', {}).get('used_mb', 0):.0f}MB used)
║ └─ Disk: {info.get('disk', {}).get('percent', 0):.1f}% full
╠═══════════════════════════════════════════════════════════╣
║ INPUT TRACKING:
║ ├─ Keyboard: {'✓ Enabled' if info.get('keyboard_available') else '✗ Disabled'}
║ ├─ Mouse: {'✓ Enabled' if info.get('mouse_available') else '✗ Disabled'}
║ └─ Tracking: {'✓ Active' if info.get('tracking_active') else '✗ Inactive'}
╠═══════════════════════════════════════════════════════════╣
║ CURRENT ACTIVITY:
║ ├─ Mouse: ({activity['mouse_position'][0]}, {activity['mouse_position'][1]})
║ ├─ Recent Keys: {len(activity['recent_keys'])} events
║ └─ Recent Text: "{activity['recent_typed_text'][:30]}"
╚═══════════════════════════════════════════════════════════╝
"""
        return report
