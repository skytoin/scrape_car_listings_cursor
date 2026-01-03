"""
Test script to verify image extraction works correctly on a single listing.
"""

import asyncio

from src.models import BrowserConfig, ScraperConfig
from src.scraper import CarsScraper


async def test_single_listing():
    """Test scraping a single listing to verify image extraction."""
    # The example URL with 4 gallery images
    url = "https://www.cars.com/vehicledetail/8492ded5-80af-44d1-b027-cbb2b4ec897d/"

    print(f"Testing image extraction from:\n{url}\n")

    config = ScraperConfig(
        browser=BrowserConfig(
            headless=False,  # Show browser to see what's happening
            slow_mo=100,
        ),
        max_retries=1,
    )

    async with CarsScraper(config) as scraper:
        print("Scraping listing...")
        listing = await scraper.scrape_listing(url)

        if listing:
            print("\n" + "=" * 60)
            print("✅ LISTING SCRAPED SUCCESSFULLY")
            print("=" * 60)
            print(f"\nCar: {listing.year} {listing.make} {listing.model}")
            print(f"Price: ${listing.price}" if listing.price else "Price: N/A")
            print(f"Mileage: {listing.mileage:,}" if listing.mileage else "Mileage: N/A")
            print(f"\n📸 IMAGES FOUND: {len(listing.images)}")
            print("=" * 60)

            if listing.images:
                for idx, img in enumerate(listing.images, 1):
                    print(f"\n{idx}. {'[PRIMARY]' if img.is_primary else '        '}")
                    print(f"   URL: {img.url}")

                    # Check if it's a valid gallery image
                    url_str = str(img.url)
                    checks = []
                    checks.append(("✅" if "/xxlarge/" in url_str or "/xlarge/" in url_str else "❌", "High quality"))
                    checks.append(("✅" if "/dealer_media/" not in url_str else "❌", "Not dealer photo"))
                    checks.append(("✅" if "/ad-creative/" not in url_str else "❌", "Not an ad"))

                    for check, desc in checks:
                        print(f"   {check} {desc}")

                print("\n" + "=" * 60)
                print("EXPECTED: 4 gallery images")
                print(f"ACTUAL:   {len(listing.images)} images")
                print("=" * 60)

                if len(listing.images) == 4:
                    print("\n✅ SUCCESS! Got exactly 4 gallery images!")
                else:
                    print(f"\n⚠️  Expected 4 images but got {len(listing.images)}")
            else:
                print("\n❌ No images found!")

        else:
            print("\n❌ Failed to scrape listing")


if __name__ == "__main__":
    asyncio.run(test_single_listing())
