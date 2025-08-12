
from __future__ import annotations
import json, os, re
from typing import Tuple
from unicodedata import normalize as uni_normalize

ALIASES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "team_aliases.json")
try:
    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        ALIASES = json.load(f)
except Exception:
    ALIASES = {}

def norm(s: str) -> str:
    s = uni_normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    s = ALIASES.get(s, s)
    return s

def match_id(league: str, date_iso: str, home: str, away: str) -> str:
    return f"{norm(league)}|{date_iso}|{norm(home)}|{norm(away)}"
