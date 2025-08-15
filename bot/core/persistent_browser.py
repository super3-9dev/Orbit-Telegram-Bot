#!/usr/bin/env python3
"""
Persistent browser manager for faster scanning.
Keeps browser running between scans to avoid startup delays.
"""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

class PersistentBrowser:
    """
    Manages a persistent browser instance to avoid startup delays.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.last_used = None
        
        # Browser configuration - ULTRA-FAST MODE
        self.browser_config = {
            'headless': False,  # Run in background for maximum performance
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded_windows',
                '--disable-renderer-backgrounding',
                '--disable-plugins',
                '--disable-extensions',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-domain-reliability',
                '--disable-dev-tools',
                '--disable-logging',
                '--disable-ipc-flooding-protection',
                # ULTRA-FAST additions (keep essential functionality)
                '--disable-images',
                '--disable-animations',
                '--disable-video',
                '--disable-audio',
                '--disable-webgl',
                '--disable-canvas-aa',
                '--disable-2d-canvas-clip-aa',
                '--disable-gl-drawing-for-tests',
                '--disable-accelerated-2d-canvas',
                '--disable-accelerated-jpeg-decoding',
                '--disable-accelerated-mjpeg-decode',
                '--disable-accelerated-video-decode',
                '--disable-gpu-rasterization',
                '--disable-software-rasterizer',
                '--disable-threaded-animation',
                '--disable-threaded-scrolling',
                '--disable-checker-imaging',
                '--disable-new-content-rendering-timeout',
                '--disable-hw-acceleration',
                '--disable-smooth-scrolling',
                '--disable-per-tab-renderer',
                '--disable-background-mode',
                '--disable-low-res-tiling',
                '--disable-composited-antialiasing',
                '--disable-partial-raster',
                '--disable-zero-copy',
                '--disable-gpu-memory-buffer-video-frames',
                '--disable-gpu-memory-buffer-compositor-resources',
                '--disable-gpu-memory-buffer-uma',
                '--disable-gpu-memory-buffer-usage-histogram'
            ]
        }
    
    async def start_browser(self) -> bool:
        """
        Start the browser if not already running.
        
        Returns:
            True if browser started successfully, False otherwise
        """
        try:
            if self.is_running and self.browser and self.context and self.page:
                print("[BROWSER] Browser already running, reusing existing instance")
                return True
            
            print("[BROWSER] Starting persistent browser...")
            
            # Start Playwright
            print("[BROWSER] Starting Playwright...")
            self.playwright = await async_playwright().start()
            print("[BROWSER] Playwright started successfully")
            
            # Launch browser
            print("[BROWSER] Launching Chromium browser...")
            self.browser = await self.playwright.chromium.launch(**self.browser_config)
            print("[BROWSER] Chromium browser launched successfully")
            
            # Create context - ULTRA-FAST MODE
            print("[BROWSER] Creating ULTRA-FAST browser context...")
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                extra_http_headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "accept-language": "en-US,en;q=0.5",
                    "accept-encoding": "gzip, deflate",
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "connection": "keep-alive",
                    "upgrade-insecure-requests": "1"
                },
                viewport={'width': 800, 'height': 600},  # Smaller viewport for speed
                ignore_https_errors=True,
                bypass_csp=True,
                java_script_enabled=True,  # Enable JS for Orbit compatibility
                has_touch=False,  # Disable touch for speed
                is_mobile=False,
                locale='en-US',
                timezone_id='UTC'
            )
            print("[BROWSER] Browser context created successfully")
            
            # Create page
            print("[BROWSER] Creating browser page...")
            self.page = await self.context.new_page()
            print("[BROWSER] Browser page created successfully")
            
            # Set page options for ULTRA-FAST loading
            print("[BROWSER] Configuring ULTRA-FAST page optimizations...")
            await self.page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Allow essential resources for proper page rendering (fully permissive for Orbit compatibility)
            await self.page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media"] else route.continue_())
            
            # Add ULTRA-FAST page optimizations
            await self.page.add_init_script("""
                // ULTRA-FAST MODE - Disable everything
                console.log = () => {};
                console.warn = () => {};
                console.error = () => {};
                
                // Disable all animations and transitions
                if (document.body) {
                    document.body.style.setProperty('animation', 'none', 'important');
                    document.body.style.setProperty('transition', 'none', 'important');
                    document.body.style.setProperty('transform', 'none', 'important');
                }
                
                // Disable all event listeners
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (['mouseover', 'mouseout', 'mousemove', 'scroll', 'resize', 'animation', 'transition'].includes(type)) {
                        return;
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                // Disable CSS animations
                const style = document.createElement('style');
                style.textContent = '* { animation: none !important; transition: none !important; transform: none !important; }';
                document.head.appendChild(style);
            """)
            
            self.is_running = True
            print("[BROWSER] ✅ Browser started successfully")
            return True
            
        except Exception as e:
            print(f"[BROWSER] ❌ Error starting browser: {e}")
            import traceback
            traceback.print_exc()
            await self.cleanup()
            return False
    
    async def get_page(self) -> Optional[Page]:
        """
        Get the current page, restarting browser if needed.
        
        Returns:
            Page instance or None if failed
        """
        try:
            # If browser is not running, start it
            if not self.is_running or not self.browser or not self.context or not self.page:
                print("[BROWSER] Browser not running, starting...")
                if not await self.start_browser():
                    return None
            
            # Check if page is still responsive
            try:
                # Simple health check - just check if page exists and is not closed
                if self.page and not self.page.is_closed():
                    # Try a simple evaluation to see if page is responsive
                    try:
                        await self.page.evaluate("() => document.readyState", timeout=2000)
                        print("[BROWSER] ✅ Page is healthy and responsive")
                        return self.page
                    except Exception as eval_error:
                        print(f"[BROWSER] Page evaluation failed: {eval_error}")
                        # Page might be unresponsive, create new one
                        await self.create_new_page()
                        return self.page
                else:
                    print("[BROWSER] Page is closed, creating new page...")
                    await self.create_new_page()
                    return self.page
                    
            except Exception as e:
                print(f"[BROWSER] Page health check failed: {e}, creating new page...")
                await self.create_new_page()
                return self.page
                
        except Exception as e:
            print(f"[BROWSER] Error getting page: {e}")
            # Try to restart the browser completely
            await self.restart_browser()
            return self.page
    
    async def create_new_page(self) -> bool:
        """
        Create a new page in the existing browser context.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.context:
                print("[BROWSER] ❌ No browser context available")
                return False
            
            # Close old page if it exists
            if self.page:
                try:
                    await self.page.close()
                except:
                    pass
                self.page = None
            
            # Wait a bit before creating new page
            await asyncio.sleep(0.5)  # Reduced wait time for speed
            
            # Create new page
            self.page = await self.context.new_page()
            
            # Set page options for ULTRA-FAST loading
            await self.page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Allow essential resources for proper page rendering (fully permissive for Orbit compatibility)
            await self.page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media"] else route.continue_())
            
            # Add ULTRA-FAST page optimizations
            await self.page.add_init_script("""
                // ULTRA-FAST MODE - Disable everything
                console.log = () => {};
                console.warn = () => {};
                console.error = () => {};
                
                // Disable all animations and transitions
                if (document.body) {
                    document.body.style.setProperty('animation', 'none', 'important');
                    document.body.style.setProperty('transition', 'none', 'important');
                    document.body.style.setProperty('transform', 'none', 'important');
                }
                
                // Disable all event listeners
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (['mouseover', 'mouseout', 'mousemove', 'scroll', 'resize', 'animation', 'transition'].includes(type)) {
                        return;
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                // Disable CSS animations
                const style = document.createElement('style');
                style.textContent = '* { animation: none !important; transition: none !important; transform: none !important; }';
                document.head.appendChild(style);
            """)
            
            print("[BROWSER] ✅ New page created successfully")
            return True
            
        except Exception as e:
            print(f"[BROWSER] Error creating new page: {e}")
            return False
    
    async def restart_browser(self) -> bool:
        """
        Restart the browser completely.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("[BROWSER] Restarting browser...")
            await self.cleanup()
            return await self.start_browser()
            
        except Exception as e:
            print(f"[BROWSER] Error restarting browser: {e}")
            return False
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                try:
                    await self.page.close()
                except:
                    pass
                self.page = None
            
            if self.context:
                try:
                    await self.context.close()
                except:
                    pass
                self.context = None
            
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
                self.browser = None
            
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
                self.playwright = None
            
            self.is_running = False
            print("[BROWSER] Cleanup completed")
            
        except Exception as e:
            print(f"[BROWSER] Error during cleanup: {e}")
    
    async def health_check(self) -> bool:
        """
        Check if the browser is healthy and responsive.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.is_running or not self.browser or not self.context or not self.page:
                return False
            
            # Check if page is closed
            if self.page.is_closed():
                return False
            
            # Try to evaluate a simple JavaScript expression with timeout
            try:
                await self.page.evaluate("() => document.readyState", timeout=3000)
                return True
            except:
                return False
                
        except Exception as e:
            print(f"[BROWSER] Health check failed: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


class BrowserManager:
    """
    Manages multiple browser instances for different sites.
    """
    
    def __init__(self):
        self.browsers: Dict[str, PersistentBrowser] = {}
        self.max_browsers = 3  # Maximum number of concurrent browsers
    
    async def get_browser(self, site_name: str) -> PersistentBrowser:
        """
        Get or create a browser for a specific site.
        
        Args:
            site_name: Name of the site (e.g., 'orbit', 'golbet')
            
        Returns:
            PersistentBrowser instance
        """
        try:
            if site_name not in self.browsers:
                if len(self.browsers) >= self.max_browsers:
                    # Close oldest browser
                    oldest_site = next(iter(self.browsers))
                    print(f"[BROWSER MANAGER] Closing oldest browser: {oldest_site}")
                    await self.browsers[oldest_site].cleanup()
                    del self.browsers[oldest_site]
                
                # Create new browser
                print(f"[BROWSER MANAGER] Creating new browser for {site_name}")
                self.browsers[site_name] = PersistentBrowser()
                success = await self.browsers[site_name].start_browser()
                if not success:
                    print(f"[BROWSER MANAGER] Failed to start browser for {site_name}")
                    return None
            else:
                # Check if existing browser is healthy
                browser = self.browsers[site_name]
                if not await browser.health_check():
                    print(f"[BROWSER MANAGER] Browser for {site_name} is unhealthy, restarting...")
                    await browser.cleanup()
                    self.browsers[site_name] = PersistentBrowser()
                    success = await self.browsers[site_name].start_browser()
                    if not success:
                        print(f"[BROWSER MANAGER] Failed to restart browser for {site_name}")
                        return None
            
            return self.browsers[site_name]
        except Exception as e:
            print(f"[BROWSER MANAGER] Error getting browser for {site_name}: {e}")
            return None
    
    async def cleanup_all(self):
        """Clean up all browser instances."""
        for site_name, browser in self.browsers.items():
            try:
                await browser.cleanup()
            except Exception as e:
                print(f"[BROWSER MANAGER] Error cleaning up {site_name}: {e}")
        
        self.browsers.clear()
        print("[BROWSER MANAGER] All browsers cleaned up")
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all browsers."""
        health_status = {}
        for site_name, browser in self.browsers.items():
            health_status[site_name] = await browser.health_check()
        
        return health_status
