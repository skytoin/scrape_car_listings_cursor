"""
Browser management for web scraping.

Handles Playwright browser lifecycle, context management, and anti-detection measures.
"""

import asyncio
import random
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fake_useragent import UserAgent
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from src.models import BrowserConfig


class BrowserManager:
    """
    Manages Playwright browser instances with anti-detection features.

    This class handles browser lifecycle, creates contexts with realistic
    settings, and implements human-like behavior patterns.

    Attributes:
        config: Browser configuration settings
        _browser: The Playwright browser instance
        _playwright: The Playwright async context manager
    """

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize browser manager.

        Args:
            config: Browser configuration settings
        """
        self.config = config
        self._browser: Browser | None = None
        self._playwright = None
        self._user_agent = UserAgent()

    async def start(self) -> None:
        """
        Start the browser instance.

        Launches Chromium with stealth settings to avoid detection.
        """
        self._playwright = await async_playwright().start()

        # Launch browser with anti-detection settings
        self._browser = await self._playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            slow_mo=self.config.slow_mo,
        )

    async def stop(self) -> None:
        """Stop the browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def create_context(self) -> BrowserContext:
        """
        Create a new browser context with realistic settings.

        Returns:
            A configured browser context

        Raises:
            RuntimeError: If browser has not been started
        """
        if not self._browser:
            raise RuntimeError("Browser not started. Call start() first.")

        # Use random user agent if not specified
        user_agent = self.config.user_agent or self._user_agent.random

        context = await self._browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            },
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            # Add realistic browser features
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
            },
        )

        # Add JavaScript to mask automation
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            window.chrome = {
                runtime: {}
            };
        """
        )

        return context

    @asynccontextmanager
    async def get_page(self) -> AsyncGenerator[Page, None]:
        """
        Create a managed page context.

        Yields:
            A configured page ready for navigation

        Example:
            async with browser_manager.get_page() as page:
                await page.goto("https://example.com")
        """
        context = await self.create_context()
        page = await context.new_page()

        # Set default timeout
        page.set_default_timeout(self.config.timeout)

        try:
            yield page
        finally:
            await page.close()
            await context.close()

    async def random_delay(self, min_seconds: float, max_seconds: float) -> None:
        """
        Add a random delay to simulate human behavior.

        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def random_mouse_movement(self, page: Page) -> None:
        """
        Simulate random mouse movements on the page.

        Args:
            page: The page to move mouse on
        """
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, self.config.viewport_width - 100)
            y = random.randint(100, self.config.viewport_height - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

    async def scroll_page(self, page: Page, scroll_times: int = 3) -> None:
        """
        Scroll the page naturally to load dynamic content.

        Args:
            page: The page to scroll
            scroll_times: Number of scroll actions to perform
        """
        for _ in range(scroll_times):
            # Scroll down
            await page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
            await asyncio.sleep(random.uniform(0.5, 1.5))

        # Scroll back to top
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(random.uniform(0.3, 0.7))
