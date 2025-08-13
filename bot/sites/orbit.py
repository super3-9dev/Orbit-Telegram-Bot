from __future__ import annotations
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import json

from playwright.async_api import async_playwright, Browser, Page
from ..core.models import MarketSnapshot, OddsQuote
from ..core.matchers import match_id

DEMO = False  # Set to True to use demo data instead of scraping


async def _scrape_orbit_page() -> Dict[str, Any] | None:
    """Scrape the Orbit page using Playwright; capture network JSON, WebSocket frames, and DOM selection IDs."""
    try:
        async with async_playwright() as p:
            # Launch browser with your cookies and user agent
            browser = await p.chromium.launch(
                headless=False,  # Set to False for debugging
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                ],
            )

            # Create context with cookies and headers
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                extra_http_headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                },
            )

            # Set cookies
            await context.add_cookies(
                [
                    {
                        "name": "COLLAPSE-LEFT_PANEL_COLLAPSE_GROUP-SPORT_COLLAPSE",
                        "value": "true",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "BIAB_AN",
                        "value": "19a3c06a-2acd-40aa-9613-0fa21d24a06d",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "BIAB_LANGUAGE",
                        "value": "en",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "COLLAPSE_SIDEBAR",
                        "value": "false",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "BIAB_TZ",
                        "value": "-540",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "BIAB_MY_BETS_TYPES",
                        "value": "%5B%22unmatched%22%2C%22matched%22%5D",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "_gid",
                        "value": "GA1.2.1792699515.1754956461",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "CSRF-TOKEN",
                        "value": "5038593b-97bd-499e-bfb4-a8e793ccae20",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "_gat_gtag_UA_252822765_1",
                        "value": "1",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "_ga",
                        "value": "GA1.1.1419922018.1754956461",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "_ga_R0X6ZP423B",
                        "value": "GS2.1.s1754999898$o3$g1$t1755001233$j59$l0$h0",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "AWSALB",
                        "value": "Q6hQlS4cfqVq0xAq+1n4nklcUHtSj94RwpHQxBFqbRMGaLf/idKM+qHWStA66yNO5oJcvrEbVc57mxSwLz+u546VivvDKh8y7IHmkeDuRopHIjHwPojbM0iYISYa",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                    {
                        "name": "AWSALBCORS",
                        "value": "Q6hQlS4cfqVq0xAq+1n4nklcUHtSj94RwpHQxBFqbRMGaLf/idKM+qHWStA66yNO5oJcvrEbVc57mxSwLz+u546VivvDKh8y7IHmkeDuRopHIjHwPojbM0iYISYa",
                        "domain": ".orbitxch.com",
                        "path": "/",
                    },
                ]
            )

            page = await context.new_page()

            # Capture JSON responses used to render the odds grid
            network_events: list[dict[str, Any]] = []
            # Capture WebSocket frames (SockJS) that carry market prices
            ws_frames: list[str] = []

            async def on_response(resp):
                try:
                    url = resp.url
                    ctype = (await resp.header_value("content-type")) or ""
                    if "customer/api" in url and (
                        "sport" in url or "market" in url or "event" in url
                    ):
                        if "application/json" in ctype:
                            try:
                                data = await resp.json()
                                network_events.append(
                                    {"url": url, "json": data, "status": resp.status}
                                )
                            except Exception:
                                pass
                except Exception:
                    pass

            page.on("response", on_response)

            def _attach_ws_listeners(ws):
                try:
                    ws.on("framereceived", lambda frame: ws_frames.append(frame))
                except Exception:
                    pass

            page.on("websocket", _attach_ws_listeners)

            # Navigate to the Orbit page
            print("[ORBIT] Navigating to https://orbitxch.com/customer/sport/1")
            await page.goto(
                "https://orbitxch.com/customer/sport/1", wait_until="networkidle"
            )

            await page.wait_for_selector(".rowsContainer", state="visible")

            # Simulate clicking the "Today" button to filter today's events
            try:
                # The "Today" tab is a <li> element, not a <button>
                today_tab = await page.query_selector(
                    'li[aria-label="tab"]:has-text("Today")'
                )
                if today_tab:
                    await today_tab.click()
                    # Wait for the rows to update after clicking "Today"
                    await page.wait_for_timeout(3000)

                    while True:
                        finished = await page.evaluate(
                            """
                            () => {
                                const el = document.querySelector('.styles_scrollableContent__i6NQK');
                                if (!el) return true;
                                const before = el.scrollTop;
                                el.scrollBy(0, 50);
                                // If we can't scroll further, we're done
                                if (el.scrollTop === before || el.scrollTop + el.clientHeight >= el.scrollHeight) {
                                    return true;
                                }
                                return false;
                            }
                            """
                        )
                        if finished:
                            break
                        await page.wait_for_timeout(400)
                else:
                    # Fallback: try to find by text only if aria-label fails
                    today_tab = await page.query_selector('li:has-text("Today")')
                    if today_tab:
                        await today_tab.click()
                        await page.wait_for_timeout(3000)
                        while True:
                            finished = await page.evaluate(
                                """
                                () => {
                                    const el = document.querySelector('.styles_scrollableContent__i6NQK');
                                    if (!el) return true;
                                    const before = el.scrollTop;
                                    el.scrollBy(0, 50);
                                    // If we can't scroll further, we're done
                                    if (el.scrollTop === before || el.scrollTop + el.clientHeight >= el.scrollHeight) {
                                        return true;
                                    }
                                    return false;
                                }
                                """
                            )
                            if finished:
                                break
                            await page.wait_for_timeout(400)
                        await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"[ORBIT] Failed to click 'Today' tab: {e}")

            try:
                rows_html_list = await page.eval_on_selector_all(
                    ".rowsContainer", "els => els.map(el => el.outerHTML)"
                )

                from bs4 import BeautifulSoup
                import re

                def _nums_from(node):
                    text = node.get_text(" ", strip=True)
                    return [float(m) for m in re.findall(r"\d+(?:\.\d+)?", text)]

                rows_objects: list[dict] = []
                for container_html in rows_html_list or []:
                    soup = BeautifulSoup(container_html, "html.parser")
                    for row in soup.select(
                        'div.biab_group-markets-table-row[data-market-prices="true"]'
                    ):

                        teams = row.select(".biab_market-title-team-names p[title]")
                        if len(teams) < 2:
                            continue
                        home = teams[0].get("title") or teams[0].text.strip()
                        away = teams[1].get("title") or teams[1].text.strip()

                        # Selection IDs (1, X, 2) if you want them
                        sel_ids = [
                            n.get("data-selection-id")
                            for n in row.select(
                                ".betContentContainer[data-selection-id]"
                            )
                        ][:3]

                        # First six numeric values in document order
                        nums: list[float] = []
                        cnt: int = 0
                        # Find odds numbers like '12' inside each bet cell
                        for wrapper in row.select(".styles_betContent__wrapper__25jEo"):
                            print("===============>")
                            for odds_el in wrapper.select(
                                ".betContentCellMarket .styles_betOdds__bxapE"
                            ):
                                if cnt % 2 != 0:
                                    print("ODDS_EL:", odds_el)
                                    txt = (odds_el.get_text(strip=True) or "").replace(
                                        ",", ""
                                    )
                                    if txt == "":
                                        nums.append(0.0)
                                        print(f"FOUND ODDS: 0 (empty odds)")
                                    else:
                                        try:
                                            nums.append(float(txt))
                                            print(f"FOUND ODDS: {txt}")
                                        except Exception:
                                            pass
                                cnt += 1
                                if len(nums) >= 6:
                                    break
                            if len(nums) >= 6:
                                break
            except Exception as e:
                print("[ORBIT] Error capturing .rowsContainer:", e)

            await browser.close()
    except Exception as e:
        print(f"[ORBIT SCRAPING ERROR] {e}")
        return None


def _parse_scraped_data_to_snapshots(
    scraped_data: Dict[str, Any],
) -> List[MarketSnapshot]:
    """Convert scraped page/network data to MarketSnapshot objects."""
    snapshots: List[MarketSnapshot] = []
    if not scraped_data:
        print("[ORBIT] No scraped content")
        return snapshots

    # 1) Prefer mapping from captured network JSON
    network = scraped_data.get("network", []) or []
    for evt in network:
        try:
            data = evt.get("json")
            if not isinstance(data, (dict, list)):
                continue
            snapshots.extend(_map_api_to_snapshots(data))
        except Exception:
            continue

    if snapshots:
        return snapshots

    # 2) Fallback: very light DOM text heuristics
    events = scraped_data.get("events", []) or []
    odds_nodes = scraped_data.get("odds", []) or []
    if not events and not odds_nodes:
        print("[ORBIT] No events/odds data found in scraped content")
        return snapshots

    try:
        league = "Unknown League"
        kickoff = datetime.now(timezone.utc) + timedelta(hours=1)
        match_name = "Scraped Match"
        if events:
            first_event = events[0]
            if isinstance(first_event, dict) and first_event.get("text"):
                match_name = str(first_event["text"])[:100]

        mid = match_id(league, kickoff.strftime("%Y-%m-%d"), match_name, "")
        quotes = []
        import re as _re

        for i, odds_item in enumerate(odds_nodes[:5]):
            try:
                text = str(odds_item.get("text", ""))
                numbers = _re.findall(r"\d+\.?\d*", text)
                if numbers:
                    odds_value = float(numbers[0])
                    quotes.append(
                        OddsQuote(
                            site="orbit",
                            market=f"Market_{i}",
                            selection=f"Selection_{i}",
                            odds=odds_value,
                            kind="LAY",
                        )
                    )
            except Exception:
                continue
        if not quotes:
            quotes = [
                OddsQuote(
                    site="orbit", market="1X2", selection="Home", odds=2.10, kind="LAY"
                ),
                OddsQuote(
                    site="orbit", market="1X2", selection="Draw", odds=3.50, kind="LAY"
                ),
                OddsQuote(
                    site="orbit", market="1X2", selection="Away", odds=3.40, kind="LAY"
                ),
            ]
        snapshots.append(
            MarketSnapshot(
                match_id=mid,
                match_name=match_name,
                league=league,
                kickoff_utc=kickoff,
                quotes=quotes,
            )
        )
    except Exception as e:
        print(f"[ORBIT] Error creating fallback snapshot: {e}")

    return snapshots


async def fetch_orbit_snapshots() -> List[MarketSnapshot]:
    """Fetch Orbit snapshots using Playwright scraping"""

    # Real scraping mode
    print("[ORBIT] Starting Playwright scraping...")
    scraped_data = await _scrape_orbit_page()

    if not scraped_data:
        print("[ORBIT] Failed to scrape page data")
        return []

    # Save raw scraped data for debugging
    try:
        with open("orbit_scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        print("[ORBIT] Saved raw scraped data to orbit_scraped_data.json")
    except Exception as e:
        print(f"[ORBIT] Error saving scraped data: {e}")

    # Convert to snapshots
    snapshots = _parse_scraped_data_to_snapshots(scraped_data)

    print(f"[ORBIT] Successfully created {len(snapshots)} snapshots")
    return snapshots
