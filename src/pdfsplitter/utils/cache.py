import json
from pathlib import Path
from typing import Optional
import hashlib
import time


class Cache:
    def __init__(self, cache_dir: Path, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()[:32]
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str) -> Optional[dict]:
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            data = json.loads(cache_path.read_text())
            if time.time() - data.get("timestamp", 0) > self.ttl_seconds:
                cache_path.unlink()
                return None
            return data.get("value")
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, value: dict):
        cache_path = self._get_cache_path(key)
        data = {"timestamp": time.time(), "value": value}
        try:
            cache_path.write_text(json.dumps(data))
        except OSError:
            pass

    def clear(self):
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                pass
