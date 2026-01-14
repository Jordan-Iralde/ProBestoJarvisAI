import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def _jarvis_data_dir() -> Path:
    data_dir = Path.home() / "Desktop" / "JarvisData"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def _consent_file() -> Path:
    return _jarvis_data_dir() / "consent.json"


def load_consent() -> Optional[Dict[str, Any]]:
    path = _consent_file()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_consent(record: Dict[str, Any]) -> None:
    path = _consent_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def get_or_request_data_collection_consent(app_name: str, app_version: str) -> bool:
    existing = load_consent()
    if isinstance(existing, dict) and "data_collection" in existing:
        return bool(existing.get("data_collection"))

    prompt = (
        f"\n{app_name} {app_version} - Consentimiento\n"
        "Jarvis puede guardar datos LOCALES en Desktop/JarvisData (logs, comandos, métricas)\n"
        "para mejorar sugerencias y debugging. Nada se envía a internet.\n"
        "¿Aceptás habilitar esta recolección local? [y/N]: "
    )

    accepted = False
    try:
        ans = input(prompt).strip().lower()
        accepted = ans in ("y", "yes", "s", "si")
    except Exception:
        accepted = False

    save_consent({
        "timestamp": datetime.now().isoformat(),
        "app": {"name": app_name, "version": app_version},
        "data_collection": accepted
    })

    return accepted
