# actions/skills/open_app.py
import subprocess
import platform


class OpenAppSkill:
    """Abre aplicaciones del sistema"""
    
    patterns = [
        r"\b(abr[ie]|open|ejecuta|launch|inicia|lanza)\b",
        r"\b(abr[ie]|open)\s+\w+",
    ]
    
    entity_hints = {
        "app": [
            "notepad", "calc", "chrome", "explorer", "cmd", "firefox", "edge",
            "brave", "vscode", "visual studio code", "code", "notas"
        ]
    }
    
    APP_ALIASES = {
        # Windows
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "terminal": "cmd.exe",
        "brave": "brave.exe",
        "vscode": "Code.exe",
        "visual studio code": "Code.exe",
        "code": "Code.exe",
        "notas": "notepad.exe",
        
        # Cross-platform
        "browser": "chrome.exe" if platform.system() == "Windows" else "firefox",
        "editor": "notepad.exe" if platform.system() == "Windows" else "gedit"
    }
    
    def run(self, entities, core):
        # Buscar app en entidades
        app_name = None
        if entities.get("app"):
            app_name = entities["app"][0] if isinstance(entities["app"], list) else entities["app"]
        
        # Fallback: si no hay app, no hacer nada (dejar que el core responda “no entendí”)
        if not app_name:
            return {"success": False, "error": "no_app_specified"}
        
        # Buscar alias
        executable = self.APP_ALIASES.get(app_name.lower(), app_name)
        
        try:
            if platform.system() == "Windows":
                subprocess.Popen(executable, shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", executable])
            else:  # Linux
                subprocess.Popen([executable])
            
            return {
                "success": True,
                "app": app_name,
                "executable": executable
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name
            }
