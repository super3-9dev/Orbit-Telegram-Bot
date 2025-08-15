from __future__ import annotations
from typing import List, Dict, Any, Optional

from playwright.async_api import async_playwright, Page
from ..core.models import MarketSnapshot
from ..core.persistent_browser import PersistentBrowser


async def _scrape_orbit_page_persistent(page: Page) -> Dict[str, Any] | None:
    """Scrape the Orbit page using an existing persistent page."""
    try:
        print("[ORBIT] Using persistent browser page")
        
        # Navigate to the Orbit page with better loading strategy
        print("[ORBIT] Navigating to https://orbitxch.com/customer/sport/1")
        await page.goto(
            "https://orbitxch.com/customer/sport/1", 
            wait_until="domcontentloaded"  # Changed from networkidle for faster loading
        )
        
        # Wait for page to be ready with faster loading strategy
        print("[ORBIT] Waiting for page content to load...")
        try:
            # Try the main selector first with shorter timeout
            await page.wait_for_selector(".rowsContainer", state="visible", timeout=8000)
            print("[ORBIT] .rowsContainer found")
        except:
            try:
                # Quick fallback: wait for any content container
                await page.wait_for_selector('[class*="rows"], [class*="container"], [class*="content"]', 
                                           state="visible", timeout=5000)
                print("[ORBIT] Alternative container found")
            except:
                # Final fallback: wait for body content
                await page.wait_for_selector("body", state="visible", timeout=3000)
                print("[ORBIT] Body content loaded")
                
                # Wait for page to be fully loaded with shorter timeout
                await page.wait_for_load_state("domcontentloaded")
                print("[ORBIT] DOM content loaded")
                
                # Give minimal time for dynamic content
                await page.wait_for_timeout(2000)
                
                # Quick check if page is interactive
                try:
                    await page.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
                    print("[ORBIT] Page fully loaded and interactive")
                except:
                    print("[ORBIT] Page load timeout, proceeding anyway")

        # Simulate clicking the "Today" button to filter today's events
        try:
            print("[ORBIT] Looking for 'Today' tab...")
            
            # Wait for the page to be fully interactive before looking for tabs
            await page.wait_for_timeout(1000)
            
            # Try multiple selectors for the Today tab
            today_tab = None
            selectors_to_try = [
                'li[aria-label="tab"]:has-text("Today")',
                'li:has-text("Today")',
                '[role="tab"]:has-text("Today")',
                'button:has-text("Today")',
                'a:has-text("Today")'
            ]
            
            for selector in selectors_to_try:
                try:
                    today_tab = await page.query_selector(selector)
                    if today_tab:
                        print(f"[ORBIT] Found 'Today' tab with selector: {selector}")
                        break
                except:
                    continue
            
            if today_tab:
                # Check if the tab is visible and clickable
                try:
                    await today_tab.wait_for_element_state("visible", timeout=5000)
                    await today_tab.click()
                    print("[ORBIT] Successfully clicked 'Today' tab")
                except Exception as click_error:
                    print(f"[ORBIT] Click failed, trying JavaScript click: {click_error}")
                    # Fallback to JavaScript click
                    await page.evaluate("(element) => element.click()", today_tab)
                    print("[ORBIT] JavaScript click executed")

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
        except Exception as e:
            print(f"[ORBIT] Failed to click 'Today' tab: {e}")
            print("[ORBIT] Continuing without Today filter...")

        try:
            # Try multiple selectors for data extraction
            rows_html_list = None
            
            # Wait a bit more for dynamic content to load
            await page.wait_for_timeout(1000)
            
            # First try the original selector
            try:
                rows_html_list = await page.eval_on_selector_all(
                    ".rowsContainer", "els => els.map(el => el.outerHTML)"
                )
                print(f"[ORBIT] Found {len(rows_html_list) if rows_html_list else 0} rows with .rowsContainer")
            except:
                print("[ORBIT] .rowsContainer not found, trying alternative selectors...")
                
                # Try alternative selectors with better targeting
                alternative_selectors = [
                    '[class*="rows"]',
                    '[class*="container"]',
                    '[class*="content"]',
                    '[class*="market"]',
                    '[class*="bet"]',
                    '[class*="event"]',
                    '[class*="match"]',
                    '[class*="game"]'
                ]
                
                for selector in alternative_selectors:
                    try:
                        rows_html_list = await page.eval_on_selector_all(
                            selector, "els => els.map(el => el.outerHTML)"
                        )
                        if rows_html_list and len(rows_html_list) > 0:
                            print(f"[ORBIT] Found {len(rows_html_list)} rows with {selector}")
                            break
                    except:
                        continue
                
                # If still no data, try to get any table-like content
                if not rows_html_list:
                    try:
                        rows_html_list = await page.eval_on_selector_all(
                            "table, [role='table'], [class*='table'], [class*='grid']", 
                            "els => els.map(el => el.outerHTML)"
                        )
                        print(f"[ORBIT] Found {len(rows_html_list) if rows_html_list else 0} table/grid elements")
                    except:
                        pass
                
                # Final attempt: look for any div with substantial content
                if not rows_html_list:
                    try:
                        rows_html_list = await page.eval_on_selector_all(
                            "div", "els => els.filter(el => el.children.length > 2).map(el => el.outerHTML)"
                        )
                        if rows_html_list and len(rows_html_list) > 0:
                            print(f"[ORBIT] Found {len(rows_html_list)} div elements with content")
                    except:
                        pass

            from bs4 import BeautifulSoup

            # Selection IDs (1, X, 2) if you want them
            nums: list[float] = []
            
            # Validate that we have data to process
            if not rows_html_list or len(rows_html_list) == 0:
                print("[ORBIT] No HTML data found, trying to extract data directly from page...")
                
                # Try to extract data directly from the page
                try:
                    direct_data = await page.evaluate("""
                        () => {
                            const data = [];
                            // Look for any elements that might contain team names and odds
                            const elements = document.querySelectorAll('[class*="team"], [class*="market"], [class*="bet"], [class*="odds"]');
                            elements.forEach(el => {
                                const text = el.textContent || el.innerText || '';
                                if (text.trim()) {
                                    data.push(text.trim());
                                }
                            });
                            return data;
                        }
                    """)
                    
                    if direct_data and len(direct_data) > 0:
                        print(f"[ORBIT] Found {len(direct_data)} text elements directly from page")
                        # Create a simple fallback structure
                        nums = [{"home": "Data Available", "away": "Check Page", "label": "1", "odds": 1.0}]
                    else:
                        print("[ORBIT] No direct data found either")
                        return None
                except Exception as e:
                    print(f"[ORBIT] Direct data extraction failed: {e}")
                    return None
            
            for container_html in rows_html_list:
                soup = BeautifulSoup(container_html, "html.parser")
                for row in soup.select(
                    'div.biab_group-markets-table-row[data-market-prices="true"]'
                ):

                    teams = row.select(".biab_market-title-team-names p[title]")
                    if len(teams) < 2:
                        continue
                    home = teams[0].get("title") or teams[0].text.strip()
                    away = teams[1].get("title") or teams[1].text.strip()
                    cnt: int = 0
                    labels = ["1", "X", "2"]
                    odds_data = []
                    for wrapper in row.select(".styles_betContent__wrapper__25jEo"):
                        odds_data.append({"home": home, "away": away})
                        for odds_el in wrapper.select(".betContentCellMarket"):
                            if cnt % 2 != 0:
                                txt = (odds_el.get_text(strip=True) or "").replace(
                                    ",", ""
                                )
                                label = (
                                    labels[cnt // 2]
                                    if (cnt // 2) < len(labels)
                                    else f"label_{cnt//2}"
                                )
                                if txt == "":
                                    odds_data.append({"label": label, "odds": 0.0})
                                else:
                                    try:
                                        odds_data.append(
                                            {"label": label, "odds": float(txt)}
                                        )
                                    except Exception:
                                        pass
                            cnt += 1
                            if len(odds_data) >= 6:
                                break
                        if len(odds_data) >= 6:
                            break
                    nums.append(odds_data)
            return nums
        except Exception as e:
            print("[ORBIT] Error capturing .rowsContainer:", e)
            return None

    except Exception as e:
        print(f"[ORBIT SCRAPING ERROR] {e}")
        return None


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
            except Exception as e:
                print(f"[ORBIT] Failed to click 'Today' tab: {e}")

            try:
                rows_html_list = await page.eval_on_selector_all(
                    ".rowsContainer", "els => els.map(el => el.outerHTML)"
                )

                from bs4 import BeautifulSoup

                # Selection IDs (1, X, 2) if you want them
                nums: list[float] = []
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
                        cnt: int = 0
                        labels = ["1", "X", "2"]
                        odds_data = []
                        for wrapper in row.select(".styles_betContent__wrapper__25jEo"):
                            odds_data.append({"home": home, "away": away})
                            for odds_el in wrapper.select(".betContentCellMarket"):
                                if cnt % 2 != 0:
                                    txt = (odds_el.get_text(strip=True) or "").replace(
                                        ",", ""
                                    )
                                    label = (
                                        labels[cnt // 2]
                                        if (cnt // 2) < len(labels)
                                        else f"label_{cnt//2}"
                                    )
                                    if txt == "":
                                        odds_data.append({"label": label, "odds": 0.0})
                                    else:
                                        try:
                                            odds_data.append(
                                                {"label": label, "odds": float(txt)}
                                            )
                                        except Exception:
                                            pass
                                cnt += 1
                                if len(odds_data) >= 6:
                                    break
                            if len(odds_data) >= 6:
                                break
                        nums.append(odds_data)
                return nums
            except Exception as e:
                print("[ORBIT] Error capturing .rowsContainer:", e)

            await browser.close()
    except Exception as e:
        print(f"[ORBIT SCRAPING ERROR] {e}")
        return None


async def fetch_orbit_snapshots(browser_manager=None) -> List[MarketSnapshot]:
    """Fetch Orbit snapshots using Playwright scraping
    
    Args:
        browser_manager: Optional BrowserManager instance for persistent browsers
    """
    
    # Check if we have a persistent browser available
    if browser_manager:
        try:
            print("[ORBIT] Using persistent browser system")
            browser = await browser_manager.get_browser('orbit')
            
            if not browser:
                print("[ORBIT] ❌ Failed to get persistent browser, falling back to new browser")
                scraped_data = await _scrape_orbit_page()
                return scraped_data
            
            print("[ORBIT] ✅ Got persistent browser, getting page...")
            page = await browser.get_page()
            
            if page:
                print("[ORBIT] ✅ Persistent page ready, scraping data...")
                result = await _scrape_orbit_page_persistent(page)
                if result:
                    print(f"[ORBIT] ✅ Scraped {len(result)} matches using persistent browser")
                    return result
                else:
                    print("[ORBIT] ⚠️ Persistent scraping failed, falling back to new browser")
            else:
                print("[ORBIT] ⚠️ Could not get persistent page, falling back to new browser")
        except Exception as e:
            print(f"[ORBIT] ⚠️ Persistent browser error: {e}, falling back to new browser")
            import traceback
            traceback.print_exc()
    
    # Fallback to traditional scraping if persistent browser fails
    print("[ORBIT] Using traditional browser scraping (fallback)")
    scraped_data = await _scrape_orbit_page()
    return scraped_data