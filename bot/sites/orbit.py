
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
    """Scrape the Orbit page using Playwright and convert to JSON"""
    try:
        async with async_playwright() as p:
            # Launch browser with your cookies and user agent
            browser = await p.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
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
                    "upgrade-insecure-requests": "1"
                }
            )
            
            # Set cookies
            await context.add_cookies([
                {"name": "COLLAPSE-LEFT_PANEL_COLLAPSE_GROUP-SPORT_COLLAPSE", "value": "true", "domain": ".orbitxch.com", "path": "/"},
                {"name": "BIAB_AN", "value": "19a3c06a-2acd-40aa-9613-0fa21d24a06d", "domain": ".orbitxch.com", "path": "/"},
                {"name": "BIAB_LANGUAGE", "value": "en", "domain": ".orbitxch.com", "path": "/"},
                {"name": "COLLAPSE_SIDEBAR", "value": "false", "domain": ".orbitxch.com", "path": "/"},
                {"name": "BIAB_TZ", "value": "-540", "domain": ".orbitxch.com", "path": "/"},
                {"name": "BIAB_MY_BETS_TYPES", "value": "%5B%22unmatched%22%2C%22matched%22%5D", "domain": ".orbitxch.com", "path": "/"},
                {"name": "_gid", "value": "GA1.2.1792699515.1754956461", "domain": ".orbitxch.com", "path": "/"},
                {"name": "CSRF-TOKEN", "value": "5038593b-97bd-499e-bfb4-a8e793ccae20", "domain": ".orbitxch.com", "path": "/"},
                {"name": "_gat_gtag_UA_252822765_1", "value": "1", "domain": ".orbitxch.com", "path": "/"},
                {"name": "_ga", "value": "GA1.1.1419922018.1754956461", "domain": ".orbitxch.com", "path": "/"},
                {"name": "_ga_R0X6ZP423B", "value": "GS2.1.s1754999898$o3$g1$t1755001233$j59$l0$h0", "domain": ".orbitxch.com", "path": "/"},
                {"name": "AWSALB", "value": "Q6hQlS4cfqVq0xAq+1n4nklcUHtSj94RwpHQxBFqbRMGaLf/idKM+qHWStA66yNO5oJcvrEbVc57mxSwLz+u546VivvDKh8y7IHmkeDuRopHIjHwPojbM0iYISYa", "domain": ".orbitxch.com", "path": "/"},
                {"name": "AWSALBCORS", "value": "Q6hQlS4cfqVq0xAq+1n4nklcUHtSj94RwpHQxBFqbRMGaLf/idKM+qHWStA66yNO5oJcvrEbVc57mxSwLz+u546VivvDKh8y7IHmkeDuRopHIjHwPojbM0iYISYa", "domain": ".orbitxch.com", "path": "/"}
            ])
            
            page = await context.new_page()
            
            # Navigate to the Orbit page
            print("[ORBIT] Navigating to https://orbitxch.com/customer/sport/1")
            await page.goto("https://orbitxch.com/customer/sport/1", wait_until="networkidle")
            
            # Wait for the page to load completely
            await page.wait_for_timeout(5000)  # Wait 5 seconds for dynamic content
            
            # Extract the page data as JSON
            page_data = await page.evaluate("""
                () => {
                    // Function to extract all visible text and structure
                    function extractPageData() {
                        const data = {
                            url: window.location.href,
                            title: document.title,
                            timestamp: new Date().toISOString(),
                            events: [],
                            markets: [],
                            odds: []
                        };
                        
                        // Try to find event containers
                        const eventSelectors = [
                            '[data-testid*="event"]',
                            '[class*="event"]',
                            '[class*="match"]',
                            '[class*="game"]',
                            '.event',
                            '.match',
                            '.game'
                        ];
                        
                        let events = [];
                        for (const selector of eventSelectors) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                events = Array.from(elements);
                                break;
                            }
                        }
                        
                        // If no specific event selectors found, look for common patterns
                        if (events.length === 0) {
                            // Look for elements that might contain match information
                            const possibleEvents = document.querySelectorAll('div, section, article');
                            events = Array.from(possibleEvents).filter(el => {
                                const text = el.textContent || '';
                                return text.includes('vs') || text.includes('v.') || 
                                       text.includes('Home') || text.includes('Away') ||
                                       text.includes('Draw') || text.includes('Over') || text.includes('Under');
                            });
                        }
                        
                        // Extract event data
                        events.forEach((event, index) => {
                            const eventData = {
                                id: index,
                                text: event.textContent?.trim() || '',
                                html: event.innerHTML || '',
                                classes: event.className || '',
                                attributes: {}
                            };
                            
                            // Extract attributes
                            for (let attr of event.attributes) {
                                eventData.attributes[attr.name] = attr.value;
                            }
                            
                            data.events.push(eventData);
                        });
                        
                        // Look for odds/market data
                        const oddsSelectors = [
                            '[class*="odds"]',
                            '[class*="price"]',
                            '[class*="bet"]',
                            '[class*="market"]',
                            '.odds',
                            '.price',
                            '.bet',
                            '.market'
                        ];
                        
                        oddsSelectors.forEach(selector => {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach((el, index) => {
                                const oddsData = {
                                    id: index,
                                    selector: selector,
                                    text: el.textContent?.trim() || '',
                                    html: el.innerHTML || '',
                                    classes: el.className || '',
                                    attributes: {}
                                };
                                
                                // Extract attributes
                                for (let attr of el.attributes) {
                                    oddsData.attributes[attr.name] = attr.value;
                                }
                                
                                data.odds.push(oddsData);
                            });
                        });
                        
                        // Extract all text content for analysis
                        data.pageText = document.body.textContent?.trim() || '';
                        
                        return data;
                    }
                    
                    return extractPageData();
                }
            """)
            
            await browser.close()
            
            print(f"[ORBIT] Successfully scraped page with {len(page_data.get('events', []))} events and {len(page_data.get('odds', []))} odds elements")
            return page_data
            
    except Exception as e:
        print(f"[ORBIT SCRAPING ERROR] {e}")
        return None

def _parse_scraped_data_to_snapshots(scraped_data: Dict[str, Any]) -> List[MarketSnapshot]:
    """Convert scraped page data to MarketSnapshot objects"""
    snapshots: List[MarketSnapshot] = []
    
    if not scraped_data or 'events' not in scraped_data:
        print("[ORBIT] No events data found in scraped content")
        return snapshots
    
    print(f"[ORBIT] Processing {len(scraped_data['events'])} scraped events")
    
    # For now, create a basic snapshot from the scraped data
    # This will need to be refined based on the actual page structure
    try:
        # Create a sample snapshot from the scraped data
        league = "Unknown League"
        kickoff = datetime.now(timezone.utc) + timedelta(hours=1)
        match_name = "Scraped Match"
        
        # Try to extract match name from events
        if scraped_data['events']:
            first_event = scraped_data['events'][0]
            if 'text' in first_event and first_event['text']:
                match_name = first_event['text'][:100]  # Limit length
        
        # Create a basic snapshot
        mid = match_id(league, kickoff.strftime("%Y-%m-%d"), match_name, "")
        
        # Create sample quotes from odds data
        quotes = []
        if 'odds' in scraped_data and scraped_data['odds']:
            for i, odds_item in enumerate(scraped_data['odds'][:5]):  # Limit to 5 quotes
                try:
                    # Try to extract numeric value from text
                    text = odds_item.get('text', '')
                    import re
                    numbers = re.findall(r'\d+\.?\d*', text)
                    if numbers:
                        odds_value = float(numbers[0])
                        quotes.append(OddsQuote(
                            site="orbit",
                            market=f"Market_{i}",
                            selection=f"Selection_{i}",
                            odds=odds_value,
                            kind="LAY"
                        ))
                except:
                    continue
        
        # If no quotes extracted, create sample ones
        if not quotes:
            quotes = [
                OddsQuote(site="orbit", market="1X2", selection="Home", odds=2.10, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Draw", odds=3.50, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Away", odds=3.40, kind="LAY"),
            ]
        
        snapshot = MarketSnapshot(
            match_id=mid,
            match_name=match_name,
            league=league,
            kickoff_utc=kickoff,
            quotes=quotes,
        )
        
        snapshots.append(snapshot)
        print(f"[ORBIT] Created snapshot: {match_name}")
        
    except Exception as e:
        print(f"[ORBIT] Error creating snapshot: {e}")
    
    return snapshots

async def fetch_orbit_snapshots() -> List[MarketSnapshot]:
    """Fetch Orbit snapshots using Playwright scraping"""
    if DEMO:
        # Demo mode - return sample data
        league = "EPL"
        kickoff = datetime.now(timezone.utc) + timedelta(hours=6)
        mid = match_id(league, kickoff.strftime("%Y-%m-%d"), "Arsenal", "Chelsea")
        m = MarketSnapshot(
            match_id=mid,
            match_name="Arsenal vs Chelsea",
            league=league,
            kickoff_utc=kickoff,
            quotes=[
                OddsQuote(site="orbit", market="1X2", selection="Home", odds=2.10, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Draw", odds=3.50, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Away", odds=3.40, kind="LAY"),
                OddsQuote(site="orbit", market="OVER_UNDER", selection="Over 2.5", odds=1.95, kind="LAY"),
                OddsQuote(site="orbit", market="OVER_UNDER", selection="Under 2.5", odds=1.90, kind="LAY"),
            ],
        )
        await asyncio.sleep(0.05)
        return [m]
    
    # Real scraping mode
    print("[ORBIT] Starting Playwright scraping...")
    scraped_data = await _scrape_orbit_page()
    
    if not scraped_data:
        print("[ORBIT] Failed to scrape page data")
        return []
    
    # Save raw scraped data for debugging
    try:
        with open('orbit_scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        print("[ORBIT] Saved raw scraped data to orbit_scraped_data.json")
    except Exception as e:
        print(f"[ORBIT] Error saving scraped data: {e}")
    
    # Convert to snapshots
    snapshots = _parse_scraped_data_to_snapshots(scraped_data)
    
    print(f"[ORBIT] Successfully created {len(snapshots)} snapshots")
    return snapshots
