
from __future__ import annotations
from typing import Iterable, Tuple, Dict
from .models import MarketSnapshot, OddsQuote
import math
import os

MIN_DIFF_ABS = float(os.getenv("MIN_DIFF_ABS", "0.00"))
MIN_DIFF_PCT = float(os.getenv("MIN_DIFF_PCT", "0.0"))  # percentage, e.g., 0.5 -> 0.5%

def pct_change(a: float, b: float) -> float:
    # percent change from other->orbit (negative is better for alert since orbit<=other)
    if b == 0:
        return 0.0
    return ((a - b) / b) * 100.0

def should_alert(orbit_odds: float, other_odds: float) -> bool:
    if orbit_odds <= 0 or other_odds <= 0:
        return False
    if orbit_odds > 999 or other_odds > 999:
        return False
    if orbit_odds > other_odds:
        return False
    # thresholds
    if MIN_DIFF_ABS > 0 and (other_odds - orbit_odds) < MIN_DIFF_ABS:
        return False
    if MIN_DIFF_PCT > 0 and abs(pct_change(orbit_odds, other_odds)) < MIN_DIFF_PCT:
        return False
    return True

def group_by_match(snapshots: Iterable[MarketSnapshot]):
    by_id: Dict[str, MarketSnapshot] = {}
    for s in snapshots:
        if s.match_id not in by_id:
            by_id[s.match_id] = s
        else:
            by_id[s.match_id].quotes.extend(s.quotes)
    return list(by_id.values())

def find_opportunities(snapshots: Iterable[MarketSnapshot]):
    # For each match/market/selection: compare Orbit LAY to any other site's odds
    matches = group_by_match(snapshots)
    for m in matches:
        # index quotes by (market, selection)
        by_key = {}
        for q in m.quotes:
            by_key.setdefault((q.market, q.selection), []).append(q)
        for (market, selection), quotes in by_key.items():
            orbit_quotes = [q for q in quotes if q.site == "orbit" and q.kind == "LAY"]
            others = [q for q in quotes if not (q.site == "orbit")]
            for o in orbit_quotes:
                for r in others:
                    if r.market != o.market or r.selection != o.selection:
                        continue
                    if should_alert(o.odds, r.odds):
                        yield m, o, r
