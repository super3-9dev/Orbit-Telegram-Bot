from __future__ import annotations
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from ..core.models import MarketSnapshot

async def _scrape_golbet724_page() -> Dict[str, Any] | None:
    """Scrape the Golbet724 page using Playwright; capture network JSON, WebSocket frames, and DOM selection IDs."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0 Safari/537.36"
            )
        )
        page = await ctx.new_page()

        # Navigate to the actual page
        print("[GOLBET] Navigating to https://www.golbet724.com/maclar")
        await page.goto("https://www.golbet724.com/maclar", wait_until="domcontentloaded")
        
        # Wait for the page to load and look for login form
        await page.wait_for_timeout(2000)
        
        try:
            # Look for login form elements
            username_input = await page.query_selector('input[type="text"][placeholder="Username"]')
            password_input = await page.query_selector('input[type="password"][placeholder="Password"]')
            login_button = await page.query_selector('input[type="submit"][value="Login"]')
            
            if username_input and password_input and login_button:
                await username_input.fill("dayı21")
                await password_input.fill("123456")
                await login_button.click()
                
                await page.wait_for_timeout(3000)
                
                try:
                    await page.wait_for_selector("select.form-control", timeout=5000)
                except:
                    print("[GOLBET] Warning: Login may have failed, continuing anyway...")
                
        except Exception as e:
            print(f"[GOLBET] Login error: {e}, continuing without authentication...")
        
        await page.wait_for_timeout(10000)
        await page.wait_for_selector("select.form-control")
        select_elem = await page.query_selector("select.form-control")
        options = await select_elem.query_selector_all("option")
        if len(options) > 1:
            value = await options[1].get_attribute("value")
            await select_elem.select_option(value)

        try:
            while True:
                finished = await page.evaluate(
                    """
                    () => {
                        const el = document.querySelector('#bultenMaclar');
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
            print(f"[GOLBET] Failed to scroll: {e}")

        rows_html_list = await page.eval_on_selector_all(
            ".oranRow", "els => els.map(el => el.outerHTML)"
        )
        await browser.close()

    nums: list[float] = []
    for row_html in rows_html_list:
        soup = BeautifulSoup(row_html, "html.parser")
        odds_data = []

        # Get team names
        team_elements = soup.select(".mac-name .mleft, .mac-name .mright")
        if len(team_elements) >= 2:
            home_team = team_elements[0].get_text(strip=True)
            away_team = team_elements[1].get_text(strip=True)
            odds_data.append({"home": home_team, "away": away_team})
        # Get only first 3 odds (1, X, 2)
        odds_elements = soup.select(".oranHover a")[:3]
        for i, odds_el in enumerate(odds_elements):
            odds_text = odds_el.get_text(strip=True)
            label = ["1", "X", "2"][i] if i < 3 else f"label_{i}"
            odds_data.append({"label": label, "odds": odds_text})
        nums.append(odds_data)
    return nums

async def fetch_golbet724_snapshots() -> List[MarketSnapshot]:
    """Fetch Golbet724 snapshots using Playwright scraping"""

    # Real scraping mode
    scraped_data = await _scrape_golbet724_page()

    return scraped_data
