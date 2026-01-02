"""
Data extraction from car listing pages.

Extracts car details, images, and metadata from individual listing pages.
"""

import re
from decimal import Decimal
from typing import Optional

from playwright.async_api import Page

from src.models import CarCondition, CarListing


class ListingExtractor:
    """
    Extracts car listing data from cars.com pages.

    This class contains methods to parse and extract structured data
    from car listing HTML using Playwright selectors.
    """

    async def extract_listing(self, page: Page, url: str) -> Optional[CarListing]:
        """
        Extract complete car listing from a page.

        Args:
            page: Playwright page with loaded listing
            url: URL of the listing

        Returns:
            CarListing object or None if extraction fails
        """
        try:
            # Wait for key elements to load
            await page.wait_for_selector("h1", timeout=10000)

            # Extract basic info from title
            title = await self._extract_title(page)
            year, make, model = self._parse_title(title)

            # Extract other fields
            price = await self._extract_price(page)
            mileage = await self._extract_mileage(page)
            condition = await self._extract_condition(page, year)
            vin = await self._extract_vin(page)
            description = await self._extract_description(page)
            location = await self._extract_location(page)
            dealer_name = await self._extract_dealer(page)

            # Extract vehicle details
            exterior_color = await self._extract_detail(page, "Exterior color")
            interior_color = await self._extract_detail(page, "Interior color")
            transmission = await self._extract_detail(page, "Transmission")
            drivetrain = await self._extract_detail(page, "Drivetrain")
            fuel_type = await self._extract_detail(page, "Fuel type")
            engine = await self._extract_detail(page, "Engine")
            mpg_city, mpg_highway = await self._extract_mpg(page)

            # Create listing object
            listing = CarListing(
                url=url,
                make=make,
                model=model,
                year=year,
                condition=condition,
                price=price,
                mileage=mileage,
                vin=vin,
                description=description,
                location=location,
                dealer_name=dealer_name,
                exterior_color=exterior_color,
                interior_color=interior_color,
                transmission=transmission,
                drivetrain=drivetrain,
                fuel_type=fuel_type,
                mpg_city=mpg_city,
                mpg_highway=mpg_highway,
                engine=engine,
            )

            # Extract images
            await self._extract_images(page, listing)

            return listing

        except Exception as e:
            print(f"Error extracting listing from {url}: {e}")
            return None

    async def _extract_title(self, page: Page) -> str:
        """Extract the main title/heading."""
        title_elem = await page.query_selector("h1")
        if title_elem:
            return await title_elem.inner_text()
        return ""

    def _parse_title(self, title: str) -> tuple[int, str, str]:
        """
        Parse year, make, and model from title.

        Args:
            title: Title string like "2020 Honda Civic"

        Returns:
            Tuple of (year, make, model)
        """
        # Match year at the beginning
        year_match = re.search(r"^(\d{4})", title.strip())
        year = int(year_match.group(1)) if year_match else 2020

        # Extract make and model
        parts = title.strip().split()
        if len(parts) >= 3:
            make = parts[1]
            model = " ".join(parts[2:])
        else:
            make = "Unknown"
            model = "Unknown"

        return year, make, model

    async def _extract_price(self, page: Page) -> Optional[Decimal]:
        """Extract price from the page."""
        # Try multiple common selectors for price
        price_selectors = [
            '[data-testid="price"]',
            ".price",
            '[class*="price"]',
            '[aria-label*="price"]',
        ]

        for selector in price_selectors:
            price_elem = await page.query_selector(selector)
            if price_elem:
                price_text = await price_elem.inner_text()
                return self._parse_price(price_text)

        return None

    def _parse_price(self, price_text: str) -> Optional[Decimal]:
        """Parse price from text string."""
        # Remove currency symbols and commas
        price_match = re.search(r"[\$]?([\d,]+)", price_text)
        if price_match:
            price_str = price_match.group(1).replace(",", "")
            return Decimal(price_str)
        return None

    async def _extract_mileage(self, page: Page) -> Optional[int]:
        """Extract mileage from the page."""
        # Common patterns for mileage
        mileage_selectors = [
            '[data-testid="mileage"]',
            ".mileage",
            '[class*="mileage"]',
        ]

        for selector in mileage_selectors:
            elem = await page.query_selector(selector)
            if elem:
                text = await elem.inner_text()
                mileage = self._parse_mileage(text)
                if mileage is not None:
                    return mileage

        # Search in all text content
        content = await page.content()
        mileage_match = re.search(r"([\d,]+)\s*miles?", content, re.IGNORECASE)
        if mileage_match:
            return int(mileage_match.group(1).replace(",", ""))

        return None

    def _parse_mileage(self, mileage_text: str) -> Optional[int]:
        """Parse mileage from text string."""
        mileage_match = re.search(r"([\d,]+)", mileage_text)
        if mileage_match:
            return int(mileage_match.group(1).replace(",", ""))
        return None

    async def _extract_condition(self, page: Page, year: int) -> CarCondition:
        """Determine car condition from page content."""
        content = await page.content()
        content_lower = content.lower()

        if "certified" in content_lower and "pre-owned" in content_lower:
            return CarCondition.CERTIFIED
        elif "new" in content_lower and year >= 2024:
            return CarCondition.NEW
        else:
            return CarCondition.USED

    async def _extract_vin(self, page: Page) -> Optional[str]:
        """Extract VIN number."""
        # Look for VIN in common locations
        vin_match = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const match = text.match(/VIN[:\\s]+([A-HJ-NPR-Z0-9]{17})/i);
                return match ? match[1] : null;
            }"""
        )
        return vin_match

    async def _extract_description(self, page: Page) -> Optional[str]:
        """Extract full description text."""
        desc_selectors = [
            '[data-testid="description"]',
            ".description",
            '[class*="description"]',
            '[class*="comments"]',
        ]

        for selector in desc_selectors:
            elem = await page.query_selector(selector)
            if elem:
                return await elem.inner_text()

        return None

    async def _extract_location(self, page: Page) -> Optional[str]:
        """Extract dealer location."""
        location_selectors = [
            '[data-testid="dealer-location"]',
            ".dealer-address",
            '[class*="location"]',
        ]

        for selector in location_selectors:
            elem = await page.query_selector(selector)
            if elem:
                return await elem.inner_text()

        return None

    async def _extract_dealer(self, page: Page) -> Optional[str]:
        """Extract dealer name."""
        dealer_selectors = [
            '[data-testid="dealer-name"]',
            ".dealer-name",
            '[class*="seller-name"]',
        ]

        for selector in dealer_selectors:
            elem = await page.query_selector(selector)
            if elem:
                return await elem.inner_text()

        return None

    async def _extract_detail(self, page: Page, detail_name: str) -> Optional[str]:
        """
        Extract a specific detail by name.

        Args:
            page: Playwright page
            detail_name: Name of the detail to extract

        Returns:
            Detail value or None
        """
        # Search for detail in structured data
        detail_value = await page.evaluate(
            f"""() => {{
                const elements = Array.from(document.querySelectorAll('dt, th, label, div'));
                for (let elem of elements) {{
                    if (elem.textContent.toLowerCase().includes('{detail_name.lower()}')) {{
                        const next = elem.nextElementSibling;
                        if (next) return next.textContent.trim();
                    }}
                }}
                return null;
            }}"""
        )
        return detail_value

    async def _extract_mpg(self, page: Page) -> tuple[Optional[int], Optional[int]]:
        """Extract city and highway MPG."""
        # Look for MPG pattern
        mpg_text = await page.evaluate(
            """() => {
                const text = document.body.innerText;
                const match = text.match(/(\\d+)\\s*city\\s*\\/\\s*(\\d+)\\s*hwy/i);
                return match ? [match[1], match[2]] : null;
            }"""
        )

        if mpg_text and len(mpg_text) == 2:
            return int(mpg_text[0]), int(mpg_text[1])

        return None, None

    async def _extract_images(self, page: Page, listing: CarListing) -> None:
        """
        Extract all image URLs from the listing.

        Args:
            page: Playwright page
            listing: CarListing to add images to
        """
        # Common image selectors
        image_selectors = [
            'img[data-testid="photo"]',
            ".vehicle-image img",
            '[class*="gallery"] img',
            '[class*="photo"] img',
            "picture img",
        ]

        seen_urls = set()
        position = 0

        for selector in image_selectors:
            images = await page.query_selector_all(selector)
            for img in images:
                # Get src or data-src (for lazy loading)
                src = await img.get_attribute("src")
                data_src = await img.get_attribute("data-src")
                url = src or data_src

                if url and url.startswith("http") and url not in seen_urls:
                    seen_urls.add(url)
                    is_primary = position == 0
                    listing.add_image(url=url, is_primary=is_primary)
                    position += 1

                if position >= 20:  # Limit to 20 images
                    break

            if position >= 20:
                break
