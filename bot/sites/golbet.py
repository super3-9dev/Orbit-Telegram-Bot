from __future__ import annotations
import os, asyncio
from typing import List
from datetime import datetime, timezone, timedelta
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ..core.models import MarketSnapshot, OddsQuote
from ..core.matchers import match_id

URL = "https://www.golbet724.com/maclar"


def _to_float(text: str) -> float | None:
    if not text:
        return None
    text = text.strip().replace(",", ".")
    m = re.search(r"\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None


async def fetch_golbet724_snapshots() -> List[MarketSnapshot]:
    snapshots: List[MarketSnapshot] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0 Safari/537.36"
            )
        )
        page = await ctx.new_page()

        # Re-render the page to ensure fresh content
        await page.goto(URL, wait_until="domcontentloaded")
        await page.evaluate(
            """(token) => { localStorage.setItem('auth_token', token); }""",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiMjc4MTgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBbHRCYXlpIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvZ2l2ZW5uYW1lIjoiZGF5xLEyMSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZ3JvdXBzaWQiOiIyNjgzMiIsImp0aSI6ImVhMDYyMDg1LWFkNzctNDZlNy04ODgwLTMzZWM3NjI0ODEwZSIsImV4cCI6MTc1NTEyNjI4MiwiaXNzIjoid3d3LnJpbzcyNC5jb20iLCJhdWQiOiJyaW83MjQuY29tIn0.MgGG1Mn7BSx05T9MqYGptPUayJ2wkUdv0fwJ8cglXxw",
        )
        await page.reload(wait_until="domcontentloaded")
        # Give the dynamic table time to render
        # Find the select element with class "form-control" and select the second option
        await page.wait_for_timeout(10000)
        await page.wait_for_selector("select.form-control")
        select_elem = await page.query_selector("select.form-control")
        options = await select_elem.query_selector_all("option")
        if len(options) > 1:
            value = await options[1].get_attribute("value")
            await select_elem.select_option(value)

        await page.wait_for_timeout(60000)
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Find a table whose header contains 1, X, 2, Under, Over, Yes, No
    target_table = None
    for tbl in soup.select("table"):
        header_cells = [
            th.get_text(strip=True).lower() for th in tbl.select("thead tr th")
        ]
        if not header_cells:
            header_cells = [
                td.get_text(strip=True).lower()
                for td in tbl.select("tr th, tr td")[:20]
            ]
        if {"1", "x", "2", "under", "over", "yes", "no"}.issubset(set(header_cells)):
            target_table = tbl
            break
    if target_table is None:
        return snapshots

    header_row = target_table.select_one("thead tr") or target_table.select("tr")[0]
    headers = [h.get_text(strip=True).lower() for h in header_row.select("th, td")]

    def col_idx(key: str) -> int | None:
        try:
            return headers.index(key)
        except Exception:
            return None

    i1, ix, i2 = col_idx("1"), col_idx("x"), col_idx("2")
    i_under, i_over = col_idx("under"), col_idx("over")
    i_yes, i_no = col_idx("yes"), col_idx("no")

    current_league = "Football"
    rows = target_table.select("tbody tr") or target_table.select("tr")[1:]
    for tr in rows:
        tds = tr.select("td")
        if not tds:
            continue

        # Detect league header rows (often use colspan)
        if any(td.has_attr("colspan") for td in tds):
            league_text = tr.get_text(" ", strip=True)
            if league_text:
                current_league = league_text
            continue

        texts = [td.get_text(" ", strip=True) for td in tds]
        non_numeric = [t for t in texts if not re.fullmatch(r"[0-9.,:+/ -]+", t)]
        if len(non_numeric) < 2:
            continue
        home, away = non_numeric[0], non_numeric[1]

        def get(i: int | None) -> float | None:
            if i is None or i >= len(tds):
                return None
            return _to_float(tds[i].get_text())

        o1, ox, o2 = get(i1), get(ix), get(i2)
        under, over = get(i_under), get(i_over)
        yes, no = get(i_yes), get(i_no)

        if not any(v is not None for v in (o1, ox, o2, over, under, yes, no)):
            continue

        kickoff = datetime.now(timezone.utc) + timedelta(
            hours=6
        )  # list page lacks exact kickoff
        mid = match_id(current_league, kickoff.strftime("%Y-%m-%d"), home, away)

        quotes: List[OddsQuote] = []
        if o1 is not None:
            quotes.append(
                OddsQuote(site="golbet724", market="1X2", selection="Home", odds=o1)
            )
        if ox is not None:
            quotes.append(
                OddsQuote(site="golbet724", market="1X2", selection="Draw", odds=ox)
            )
        if o2 is not None:
            quotes.append(
                OddsQuote(site="golbet724", market="1X2", selection="Away", odds=o2)
            )
        if over is not None:
            quotes.append(
                OddsQuote(
                    site="golbet724", market="OVER_UNDER", selection="Over", odds=over
                )
            )
        if under is not None:
            quotes.append(
                OddsQuote(
                    site="golbet724", market="OVER_UNDER", selection="Under", odds=under
                )
            )
        if yes is not None:
            quotes.append(
                OddsQuote(site="golbet724", market="BTTS", selection="Yes", odds=yes)
            )
        if no is not None:
            quotes.append(
                OddsQuote(site="golbet724", market="BTTS", selection="No", odds=no)
            )

        snapshots.append(
            MarketSnapshot(
                match_id=mid,
                match_name=f"{home} vs {away}",
                league=current_league,
                kickoff_utc=kickoff,
                quotes=quotes,
            )
        )

    return snapshots
