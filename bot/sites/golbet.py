from __future__ import annotations
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
from ..core.models import MarketSnapshot
from ..core.persistent_browser import PersistentBrowser


async def _scrape_golbet724_page_persistent(page: Page) -> Dict[str, Any] | None:
    """Scrape the Golbet724 page using an existing persistent page."""
    try:
        print("[GOLBET] Using persistent browser page")
        
        # Navigate to the actual page
        print("[GOLBET] Navigating to https://www.golbet724.com/maclar")
        await page.goto("https://www.golbet724.com/maclar", wait_until="domcontentloaded")
        
        # Check if we're on a redirect page
        redirect_text = await page.evaluate("() => document.body.innerText")
        if "Redirecting" in redirect_text:
            print("[GOLBET] Detected redirect page, waiting for completion...")
            await page.wait_for_timeout(5000)
            # Try to wait for actual content
            try:
                await page.wait_for_selector("select.form-control", timeout=10000)
                print("[GOLBET] Redirect completed, content loaded")
            except:
                print("[GOLBET] Redirect timeout, continuing anyway...")
        
        await page.wait_for_timeout(5000)
        try:
            # Look for login form elements
            username_input = await page.query_selector('input[type="text"][placeholder="Username"]')
            password_input = await page.query_selector('input[type="password"][placeholder="Password"]')
            login_button = await page.query_selector('input[type="submit"][value="Login"]')
            
            if username_input and password_input and login_button:
                await username_input.fill("dayı21")
                await password_input.fill("123456")
                await login_button.click()
                
        except Exception as e:
            print(f"[GOLBET] Login error: {e}, continuing without authentication...")
        
        await page.wait_for_timeout(2000)
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
        
        await page.wait_for_timeout(5000)
        rows_html_list = await page.eval_on_selector_all(
            ".oranRow", "els => els.map(el => el.outerHTML)"    
        )

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
        
    except Exception as e:
        print(f"[GOLBET SCRAPING ERROR] {e}")
        return None


async def _scrape_golbet724_page() -> Dict[str, Any] | None:
    """Scrape the Golbet724 page using Playwright; capture network JSON, WebSocket frames, and DOM selection IDs."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, 
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
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0 Safari/537.36",
            ),
            extra_http_headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
            },
        )
        page = await ctx.new_page()

        # Navigate to the actual page
        print("[GOLBET] Navigating to https://www.golbet724.com/maclar")
        await page.goto("https://www.golbet724.com/maclar", wait_until="domcontentloaded")
        
        try:
            # Look for login form elements
            username_input = await page.query_selector('input[type="text"][placeholder="Username"]')
            password_input = await page.query_selector('input[type="password"][placeholder="Password"]')
            login_button = await page.query_selector('input[type="submit"][value="Login"]')
            
            if username_input and password_input and login_button:
                await username_input.fill("dayı21")
                await password_input.fill("123456")
                await login_button.click()
                
        except Exception as e:
            print(f"[GOLBET] Login error: {e}, continuing without authentication...")
        
        await page.wait_for_timeout(2000)
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
                        el.scrollBy(0, 100);
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

        await page.wait_for_timeout(5000)
        rows_html_list = await page.eval_on_selector_all(
            ".oranRow", "els => els.map(el => el.outerHTML)"
        )

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

async def fetch_golbet724_snapshots(browser_manager=None) -> List[MarketSnapshot]:
    """Fetch Golbet724 snapshots using Playwright scraping
    
    Args:
        browser_manager: Optional BrowserManager instance for persistent browsers
    """
    
    # Check if we have a persistent browser available
    if browser_manager:
        try:
            print("[GOLBET] Using persistent browser system")
            browser = await browser_manager.get_browser('golbet')
            page = await browser.get_page()
            
            if page:
                print("[GOLBET] ✅ Persistent page ready, scraping data...")
                result = await _scrape_golbet724_page_persistent(page)
                if result:
                    print(f"[GOLBET] ✅ Scraped {len(result)} matches using persistent browser")
                    return result
                else:
                    print("[GOLBET] ⚠️ Persistent scraping failed, falling back to new browser")
            else:
                print("[GOLBET] ⚠️ Could not get persistent page, falling back to new browser")
        except Exception as e:
            print(f"[GOLBET] ⚠️ Persistent browser error: {e}, falling back to new browser")
    
    # Fallback to traditional scraping if persistent browser fails
    print("[GOLBET] Using traditional browser scraping (fallback)")
    scraped_data = await _scrape_golbet724_page()
    return scraped_data
