"""
Main scraper orchestrator for cars.com.

Coordinates browser management, page navigation, and data extraction
with parallelization and retry logic.
"""

import asyncio
from pathlib import Path
from typing import Optional

import httpx
from playwright.async_api import Page

from src.models import CarListing, ScraperConfig
from src.scraper.browser_manager import BrowserManager
from src.scraper.listing_extractor import ListingExtractor


class CarsScraper:
    """
    Main scraper for cars.com listings.

    Orchestrates the scraping process including browser management,
    parallel scraping, retry logic, and optional image downloads.

    Attributes:
        config: Scraper configuration
        browser_manager: Manages browser instances
        extractor: Extracts data from pages
    """

    def __init__(self, config: Optional[ScraperConfig] = None) -> None:
        """
        Initialize the scraper.

        Args:
            config: Scraper configuration (uses defaults if None)
        """
        self.config = config or ScraperConfig()
        self.browser_manager = BrowserManager(self.config.browser)
        self.extractor = ListingExtractor()
        self._httpx_client: Optional[httpx.AsyncClient] = None

    async def start(self) -> None:
        """Start the scraper and initialize resources."""
        await self.browser_manager.start()
        self._httpx_client = httpx.AsyncClient(timeout=30.0)

        # Create image directory if needed
        if self.config.save_images:
            Path(self.config.image_directory).mkdir(parents=True, exist_ok=True)

    async def stop(self) -> None:
        """Stop the scraper and cleanup resources."""
        await self.browser_manager.stop()
        if self._httpx_client:
            await self._httpx_client.aclose()

    async def scrape_search_page(self, url: str) -> list[CarListing]:
        """
        Scrape all listings from a search results page.

        Args:
            url: URL of the search results page

        Returns:
            List of scraped car listings
        """
        listings: list[CarListing] = []

        async with self.browser_manager.get_page() as page:
            # Navigate to search page
            await page.goto(url, wait_until="domcontentloaded")
            await self.browser_manager.random_delay(
                self.config.min_delay_seconds, self.config.max_delay_seconds
            )

            # Scroll to load dynamic content
            await self.browser_manager.scroll_page(page)

            # Extract listing URLs
            listing_urls = await self._extract_listing_urls(page)
            listing_urls = listing_urls[: self.config.max_listings_per_page]

            print(f"Found {len(listing_urls)} listings on page")

        # Scrape listings in parallel with semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.config.max_concurrent_pages)
        tasks = [self._scrape_with_semaphore(semaphore, url) for url in listing_urls]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        for result in results:
            if isinstance(result, CarListing):
                listings.append(result)
            elif isinstance(result, Exception):
                print(f"Error during scraping: {result}")

        return listings

    async def _scrape_with_semaphore(
        self, semaphore: asyncio.Semaphore, url: str
    ) -> Optional[CarListing]:
        """
        Scrape a single listing with semaphore rate limiting.

        Args:
            semaphore: Asyncio semaphore for rate limiting
            url: URL of the listing to scrape

        Returns:
            Scraped listing or None if failed
        """
        async with semaphore:
            return await self.scrape_listing(url)

    async def scrape_listing(self, url: str) -> Optional[CarListing]:
        """
        Scrape a single car listing with retry logic.

        Args:
            url: URL of the listing page

        Returns:
            CarListing object or None if scraping fails
        """
        for attempt in range(self.config.max_retries):
            try:
                async with self.browser_manager.get_page() as page:
                    # Navigate to listing
                    await page.goto(url, wait_until="domcontentloaded")

                    # Add random delay
                    await self.browser_manager.random_delay(
                        self.config.min_delay_seconds, self.config.max_delay_seconds
                    )

                    # Random mouse movement for realism
                    await self.browser_manager.random_mouse_movement(page)

                    # Extract listing data
                    listing = await self.extractor.extract_listing(page, url)

                    if listing and self.config.save_images:
                        await self._download_images(listing)

                    return listing

            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                else:
                    return None

        return None

    async def _extract_listing_urls(self, page: Page) -> list[str]:
        """
        Extract all listing URLs from a search results page.

        Args:
            page: Playwright page with search results

        Returns:
            List of listing URLs
        """
        # Common selectors for listing links
        selectors = [
            'a[href*="/vehicledetail/"]',
            'a[data-testid="listing-link"]',
            '.vehicle-card a[href*="/detail/"]',
            'a[class*="vehicle-card-link"]',
        ]

        urls = []
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            for elem in elements:
                href = await elem.get_attribute("href")
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        href = f"https://www.cars.com{href}"
                    if href not in urls and "cars.com" in href:
                        urls.append(href)

        # Fallback: find any links that look like listing pages
        if not urls:
            all_links = await page.query_selector_all("a[href]")
            for link in all_links:
                href = await link.get_attribute("href")
                if href and ("vehicledetail" in href or "/detail/" in href) and href not in urls:
                    if href.startswith("/"):
                        href = f"https://www.cars.com{href}"
                    urls.append(href)

        return urls

    async def _download_images(self, listing: CarListing) -> None:
        """
        Download images for a listing to local storage.

        Args:
            listing: CarListing with image URLs to download
        """
        if not self._httpx_client:
            return

        image_dir = Path(self.config.image_directory) / str(listing.listing_id)
        image_dir.mkdir(parents=True, exist_ok=True)

        for idx, image in enumerate(listing.images):
            try:
                response = await self._httpx_client.get(str(image.url))
                response.raise_for_status()

                # Determine file extension from URL or content-type
                extension = self._get_image_extension(
                    str(image.url), response.headers.get("content-type", "")
                )
                filename = f"image_{idx:02d}{extension}"
                filepath = image_dir / filename

                # Save image
                filepath.write_bytes(response.content)

                # Update image model with local path
                image.local_path = str(filepath)

            except Exception as e:
                print(f"Failed to download image {image.url}: {e}")

    def _get_image_extension(self, url: str, content_type: str) -> str:
        """
        Determine image file extension.

        Args:
            url: Image URL
            content_type: HTTP content-type header

        Returns:
            File extension including dot (e.g., '.jpg')
        """
        # Try to get from URL
        if url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            return url[url.rfind(".") :]

        # Try to get from content-type
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
        elif "png" in content_type:
            return ".png"
        elif "webp" in content_type:
            return ".webp"
        elif "gif" in content_type:
            return ".gif"

        # Default to jpg
        return ".jpg"

    async def __aenter__(self) -> "CarsScraper":
        """Enable async context manager usage."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Cleanup when exiting context manager."""
        await self.stop()
