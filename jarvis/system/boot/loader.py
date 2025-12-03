# system/boot/loader.py
import importlib.util
import os
import sys
import traceback

class ModuleLoader:
    def __init__(self, core, modules_path=None):
        self.core = core
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # system/boot -> system
        self.modules_path = modules_path or os.path.join(base, "..", "modules", "installed")
        self.loaded = []

    def load_all(self):
        path = os.path.abspath(self.modules_path)
        if not os.path.isdir(path):
            self.core._log("MODULES", f"No modules folder at {path}")
            return
        for name in os.listdir(path):
            mod_dir = os.path.join(path, name)
            module_py = os.path.join(mod_dir, "module.py")
            if os.path.isfile(module_py):
                try:
                    spec = importlib.util.spec_from_file_location(f"modules.{name}", module_py)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    # expected interface: setup(core) -> returns module handle with stop()
                    handle = getattr(mod, "setup")(self.core)
                    self.loaded.append((name, handle))
                    self.core._log("MODULE", f"Loaded module {name}")
                except Exception:
                    self.core._log("MODULE_ERROR", f"Failed loading {name}")
                    traceback.print_exc()

    def stop_all(self):
        for name, handle in self.loaded:
            try:
                stop_fn = getattr(handle, "stop", None)
                if callable(stop_fn):
                    stop_fn()
                    self.core._log("MODULE", f"Stopped module {name}")
            except Exception:
                traceback.print_exc()
