# skills/productivity/open_app_advanced.py
"""
Advanced App Opener - Better app detection and execution
Searches: Registry, common paths, PATH env, app shortcuts
"""

import os
import subprocess
import sys
import winreg  # Windows registry
from pathlib import Path
from typing import Optional, Dict, List


class AppFinder:
    """Finds installed applications on Windows"""
    
    COMMON_PATHS = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\Users\\{user}\\AppData\\Local\\Programs",
        "C:\\ProgramData",
    ]
    
    APP_NAMES_MAP = {
        "obsidian": ["obsidian.exe", "Obsidian"],
        "visual studio code": ["code.exe", "Code.exe"],
        "vscode": ["code.exe", "Code.exe"],
        "explorer": ["explorer.exe"],
        "file explorer": ["explorer.exe"],
        "chrome": ["chrome.exe", "Google Chrome"],
        "edge": ["msedge.exe", "Microsoft Edge"],
        "firefox": ["firefox.exe", "Mozilla Firefox"],
        "spotify": ["spotify.exe", "Spotify"],
        "discord": ["discord.exe", "Discord"],
        "slack": ["slack.exe", "Slack"],
        "telegram": ["telegram.exe", "Telegram"],
        "whatsapp": ["whatsapp.exe", "WhatsApp"],
        "notion": ["notion.exe", "Notion"],
        "mongodb": ["mongod.exe", "MongoDB"],
        "docker": ["docker.exe", "Docker"],
        "git": ["git.exe", "Git"],
        "python": ["python.exe", "Python"],
        "node": ["node.exe", "Node.js"],
        "postman": ["postman.exe", "Postman"],
        "mongodb compass": ["MongoDB Compass.exe"],
        "sqlserver": ["sqlserver.exe", "SQL Server"],
        "mysql": ["mysql.exe", "MySQL"],
    }
    
    def __init__(self):
        self.app_cache = {}
    
    def find_app(self, app_name: str) -> Optional[str]:
        """Find full path to an application"""
        
        # Check cache first
        if app_name in self.app_cache:
            path = self.app_cache[app_name]
            if os.path.exists(path):
                return path
        
        # Try direct paths from mapping
        if app_name.lower() in self.APP_NAMES_MAP:
            executables = self.APP_NAMES_MAP[app_name.lower()]
            
            for exe in executables:
                # Check registry
                path = self._search_registry(exe)
                if path:
                    self.app_cache[app_name] = path
                    return path
                
                # Check common paths
                path = self._search_paths(exe)
                if path:
                    self.app_cache[app_name] = path
                    return path
        
        # Fuzzy search if direct match fails
        path = self._fuzzy_search(app_name)
        if path:
            self.app_cache[app_name] = path
            return path
        
        # Check in PATH environment variable
        path = self._search_env_path(app_name)
        if path:
            self.app_cache[app_name] = path
            return path
        
        return None
    
    def _search_registry(self, app_name: str) -> Optional[str]:
        """Search Windows registry for application"""
        try:
            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            
                            if app_name.lower() in display_name.lower():
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                
                                # Search for exe in install location
                                exe_path = os.path.join(install_location, f"{app_name}.exe")
                                if os.path.exists(exe_path):
                                    return exe_path
                        
                        i += 1
                    except WindowsError:
                        break
        except Exception:
            pass
        
        return None
    
    def _search_paths(self, executable: str) -> Optional[str]:
        """Search common installation paths"""
        username = os.getenv("USERNAME", "User")
        
        for base_path in self.COMMON_PATHS:
            # Replace {user} placeholder
            base_path = base_path.replace("{user}", username)
            
            # Direct exe
            path = os.path.join(base_path, executable)
            if os.path.exists(path):
                return path
            
            # Recursive search (max 2 levels)
            for root, dirs, files in os.walk(base_path):
                # Limit depth
                if root.count(os.sep) - base_path.count(os.sep) > 2:
                    continue
                
                if executable.lower() in [f.lower() for f in files]:
                    return os.path.join(root, executable)
        
        return None
    
    def _search_env_path(self, app_name: str) -> Optional[str]:
        """Search PATH environment variable"""
        path_env = os.getenv("PATH", "")
        
        for path_dir in path_env.split(os.pathsep):
            exe_path = os.path.join(path_dir, f"{app_name}.exe")
            if os.path.exists(exe_path):
                return exe_path
        
        return None
    
    def _fuzzy_search(self, app_name: str) -> Optional[str]:
        """Fuzzy search for application"""
        # Try common locations with app name variations
        variations = [
            f"{app_name}.exe",
            f"{app_name.title()}.exe",
            f"{app_name.upper()}.exe",
        ]
        
        for var in variations:
            path = self._search_paths(var)
            if path:
                return path
        
        return None


class OpenAppAdvancedSkill:
    """Open applications with advanced detection"""
    
    patterns = [
        r".*abrir.*",
        r".*abre.*",
        r".*inicia.*",
        r".*ejecuta.*",
        r".*lanza.*",
        r".*open.*",
        r".*launch.*",
    ]
    
    def __init__(self):
        self.name = "open_app_advanced"
        self.finder = AppFinder()
    
    def run(self, entities, core=None):
        """Execute app opening with advanced detection"""
        
        if not entities.get("app"):
            return {"success": False, "error": "No app specified"}
        
        app_name = entities["app"][0]
        
        # Try to find the app
        app_path = self.finder.find_app(app_name)
        
        if not app_path:
            return {
                "success": False,
                "error": f"Could not find application: {app_name}",
                "suggestions": self._get_suggestions(app_name)
            }
        
        # Try to execute
        try:
            if app_name.lower() == "explorer":
                os.startfile(app_path)
            else:
                subprocess.Popen(app_path)
            
            # Learn this path for future use
            if core and hasattr(core, 'adaptive_memory'):
                core.adaptive_memory.record_app_path(app_name, app_path, confidence=0.95)
            
            return {
                "success": True,
                "message": f"Opening {app_name}...",
                "app": app_name,
                "path": app_path
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name,
                "path": app_path
            }
    
    def _get_suggestions(self, app_name: str) -> List[str]:
        """Get suggestions for app not found"""
        suggestions = []
        
        # Check if it's a typo
        for known_app in self.finder.APP_NAMES_MAP.keys():
            if self._similarity(app_name, known_app) > 0.7:
                suggestions.append(f"Did you mean: {known_app}?")
        
        return suggestions
    
    def _similarity(self, a: str, b: str) -> float:
        """Simple string similarity"""
        a, b = a.lower(), b.lower()
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / max(len(a), len(b), 1)
