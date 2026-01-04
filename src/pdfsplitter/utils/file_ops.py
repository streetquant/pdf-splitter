import magic
from pathlib import Path
from typing import Literal


def detect_file_type(file_path: Path) -> Literal["pdf", "epub", "unknown"]:
    mime = magic.from_file(str(file_path), mime=True)

    if "pdf" in mime:
        return "pdf"
    elif "epub" in mime or "zip" in mime:
        if file_path.suffix.lower() == ".epub":
            return "epub"
    elif "application" in mime or "octet-stream" in mime:
        if file_path.suffix.lower() == ".epub":
            return "epub"
    return "unknown"


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    import re

    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.strip()
    return name if name else "unnamed"
