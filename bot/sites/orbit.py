
from __future__ import annotations
import os, asyncio, json
from typing import List, Dict
from datetime import datetime, timezone, timedelta
import httpx, orjson

from ..core.models import MarketSnapshot, OddsQuote
from ..core.matchers import match_id

DEMO = os.getenv("DEMO", "1") == "1"


def _parse_cookie_string(cookie_str: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    if not cookie_str:
        return cookies
    for part in cookie_str.split(";"):
        if not part.strip():
            continue
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        cookies[name.strip()] = value.strip()
    return cookies


def _api_url() -> str:
    return os.getenv("ORBIT_API_URL", "https://orbitxch.com/customer/api/sport/details")


def _api_params() -> Dict[str, str]:
    return {
        "page": os.getenv("ORBIT_API_PAGE", "0"),
        "size": os.getenv("ORBIT_API_SIZE", "20"),
    }


def _api_payload() -> Dict[str, str]:
    # Allow full override via env; otherwise use the payload seen in your screenshots
    override = os.getenv("ORBIT_API_PAYLOAD_JSON", "").strip()
    if override:
        try:
            return json.loads(override)
        except Exception:
            print("[ORBIT API] Invalid ORBIT_API_PAYLOAD_JSON; falling back to default")
    return {
        "viewBy": "TIME",
        "timeFilter": "TODAY",
        "id": "1",
        "contextFilter": "EVENT_TYPE",
    }


def _headers() -> Dict[str, str]:
    ua = os.getenv(
        "ORBIT_UA",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    )
    csrf = os.getenv("ORBIT_CSRF", "")
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://orbitxch.com",
        "referer": "https://orbitxch.com/customer/sport/1",
        "user-agent": ua,
        "x-device": "DESKTOP",
    }
    if csrf:
        headers["x-csrf-token"] = csrf
    # Optional extra headers via JSON
    extra_json = os.getenv("ORBIT_HEADERS_JSON", "").strip()
    if extra_json:
        try:
            headers.update(json.loads(extra_json))
        except Exception:
            print("[ORBIT API] Invalid ORBIT_HEADERS_JSON; ignoring")
    return headers


def _client_kwargs() -> Dict:
    # Default to HTTP/1.1. Enable HTTP/2 only if explicitly requested and you have httpx[http2] installed.
    use_http2 = os.getenv("ORBIT_HTTP2", "false").lower() == "true"
    kwargs: Dict = {"timeout": 15.0, "headers": _headers()}
    if use_http2:
        kwargs["http2"] = True
    cookie_str = os.getenv("ORBIT_COOKIES", os.getenv("ORBIT_COOKIE", ""))
    cookies = _parse_cookie_string(cookie_str)
    if cookies:
        kwargs["cookies"] = cookies
    use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
    http_proxy = os.getenv("HTTP_PROXY", "").strip()
    if use_proxy and http_proxy:
        kwargs["proxies"] = {"http://": http_proxy, "https://": http_proxy}
    return kwargs


async def _fetch_api_json() -> dict | None:
    url = _api_url()
    params = _api_params()
    payload = _api_payload()
    try:
        async with httpx.AsyncClient(**_client_kwargs()) as client:
            resp = await client.post(url, params=params, json=payload, follow_redirects=True)
            resp.raise_for_status()
            # Prefer orjson for speed, fallback to .json()
            try:
                return orjson.loads(resp.content)
            except Exception:
                return resp.json()
    except httpx.HTTPStatusError as e:
        print("[ORBIT API HTTP]", e.response.status_code, e)
    except Exception as e:
        print("[ORBIT API ERROR]", e)
    return None


def _safe_parse_datetime(value) -> datetime | None:
    if value is None:
        return None
    try:
        # Epoch ms or s
        if isinstance(value, (int, float)):
            ts = float(value)
            if ts > 1e12:
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        # ISO8601
        if isinstance(value, str):
            # Strip timezone Z if present; datetime.fromisoformat handles offsets
            s = value.strip()
            try:
                if s.endswith("Z"):
                    s = s[:-1] + "+00:00"
                return datetime.fromisoformat(s)
            except Exception:
                return None
    except Exception:
        return None
    return None


def _extract_first(obj: dict, keys: list[str]):
    for k in keys:
        if k in obj and obj[k] not in (None, ""):
            return obj[k]
    return None


def _find_lists_by_keys(obj: dict, candidate_keys: list[str]) -> list[list[dict]]:
    found: list[list[dict]] = []
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for key, val in cur.items():
                if isinstance(val, list) and key.lower() in candidate_keys and val and isinstance(val[0], dict):
                    found.append(val)    
                elif isinstance(val, (dict, list)):
                    stack.append(val)
        elif isinstance(cur, list):
            for item in cur:
                if isinstance(item, (dict, list)):
                    stack.append(item)
    return found


def _map_api_to_snapshots(api: dict) -> List[MarketSnapshot]:
    # Log small preview once
    try:
        preview = orjson.dumps(api)
        s = preview.decode("utf-8") if isinstance(preview, bytes) else str(preview)
        print("[ORBIT API PREVIEW]", (s[:800] + "...") if len(s) > 800 else s)
    except Exception:
        pass

    # Heuristic mapping for common schemas
    snapshots: list[MarketSnapshot] = []

    # 1) Find top-level list of events; try common containers
    candidate_lists = _find_lists_by_keys(api, [
        "events", "content", "items", "matches", "data", "list"
    ])
    # Also check if api itself is a list of events
    if isinstance(api, list) and api and isinstance(api[0], dict):
        candidate_lists.insert(0, api)  # prioritize top-level

    if not candidate_lists:
        return snapshots

    events = candidate_lists[0]

    for ev in events:
        if not isinstance(ev, dict):
            continue
        league = _extract_first(ev, ["league", "competition", "tournament", "leagueName"]) or None
        # Build match name
        home = _extract_first(ev, ["home", "homeTeam", "teamHome", "home_name"]) or None
        away = _extract_first(ev, ["away", "awayTeam", "teamAway", "away_name"]) or None
        name = _extract_first(ev, ["name", "match", "eventName"]) or None
        if not name and home and away:
            name = f"{home} vs {away}"

        kickoff = _safe_parse_datetime(
            _extract_first(ev, ["startTime", "kickoff", "start", "start_ts", "date"])
        )

        if not name:
            # Skip events without a resolvable name
            continue

        # Markets container
        markets_lists = _find_lists_by_keys(ev, ["markets", "marketList", "mkt", "bettingMarkets"]) or []
        quotes: list[OddsQuote] = []

        for markets in markets_lists:
            for mk in markets:
                if not isinstance(mk, dict):
                    continue
                market_name = _extract_first(mk, ["market", "name", "marketName", "marketType"]) or "UNKNOWN"
                # Selections container
                sel_lists = _find_lists_by_keys(mk, ["selections", "runners", "outcomes", "legs"]) or []
                for sels in sel_lists:
                    for sel in sels:
                        if not isinstance(sel, dict):
                            continue
                        selection_name = _extract_first(sel, ["name", "selection", "runnerName", "label"]) or "UNKNOWN"
                        # Lay price keys
                        price = _extract_first(sel, [
                            "lay", "layPrice", "layOdds", "bestLay", "lay_price", "layOddsPrice",
                        ])
                        # If price is a dict/array, try inner common keys
                        if isinstance(price, dict):
                            price = _extract_first(price, ["price", "odds", "value"]) or price.get("0")
                        if isinstance(price, list) and price:
                            price = price[0]
                        try:
                            if price is not None:
                                price_f = float(price)
                                quotes.append(OddsQuote(site="orbit", market=market_name, selection=selection_name, odds=price_f, kind="LAY"))
                        except Exception:
                            continue

        if quotes:
            # Use league/home/away for match_id when possible; fall back to name
            league_for_id = league or ""
            date_for_id = (kickoff or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
            if home and away:
                mid = match_id(league_for_id or "", date_for_id, home, away)
            else:
                mid = match_id(league_for_id or "", date_for_id, name, "")
            snapshots.append(MarketSnapshot(
                match_id=mid,
                match_name=name,
                league=league,
                kickoff_utc=kickoff,
                quotes=quotes,
            ))

    return snapshots


async def fetch_orbit_snapshots() -> List[MarketSnapshot]:
    # if DEMO:
    #     # Simulated: Orbit LAY odds for one match
    #     league = "EPL"
    #     kickoff = datetime.now(timezone.utc) + timedelta(hours=6)
    #     mid = match_id(league, kickoff.strftime("%Y-%m-%d"), "Arsenal", "Chelsea")
    #     m = MarketSnapshot(
    #         match_id=mid,
    #         match_name="Arsenal vs Chelsea",
    #         league=league,
    #         kickoff_utc=kickoff,
    #         quotes=[
    #             OddsQuote(site="orbit", market="1X2", selection="Home", odds=2.10, kind="LAY"),
    #             OddsQuote(site="orbit", market="1X2", selection="Draw", odds=3.50, kind="LAY"),
    #             OddsQuote(site="orbit", market="1X2", selection="Away", odds=3.40, kind="LAY"),
    #             OddsQuote(site="orbit", market="OVER_UNDER", selection="Over 2.5", odds=1.95, kind="LAY"),
    #             OddsQuote(site="orbit", market="OVER_UNDER", selection="Under 2.5", odds=1.90, kind="LAY"),
    #         ],
    #     )
    #     await asyncio.sleep(0.05)
    #     return [m]

    api = await _fetch_api_json()
    print(api)
    if not api:
        return []
    return _map_api_to_snapshots(api)
