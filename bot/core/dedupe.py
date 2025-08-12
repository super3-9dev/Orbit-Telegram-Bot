
from __future__ import annotations
import time
from typing import Dict, Tuple

class DedupeCache:
    def __init__(self, window_seconds: int = 600):
        self.window = window_seconds
        self._seen: Dict[str, float] = {}

    def _key(self, match_id: str, market: str, selection: str) -> str:
        return f"{match_id}|{market}|{selection}"

    def seen_recently(self, match_id: str, market: str, selection: str) -> bool:
        k = self._key(match_id, market, selection)
        now = time.time()
        ts = self._seen.get(k)
        if ts is None:
            return False
        return (now - ts) < self.window

    def mark(self, match_id: str, market: str, selection: str):
        self._seen[self._key(match_id, market, selection)] = time.time()
