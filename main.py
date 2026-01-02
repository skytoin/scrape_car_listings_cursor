"""
Main entry point for the cars.com scraper.

Run this file to scrape car listings with custom make, model, and year filters.
Results are saved in hierarchical folder structure: data/make/model/listing_id/
"""

import asyncio

from src.models import BrowserConfig, ScraperConfig
from src.scraper import CarsScraper
from src.utils import save_hierarchical


# ========================================
# CUSTOMIZE YOUR SEARCH HERE
# ========================================

# Car make (e.g., "toyota", "bmw", "honda", "ford", "chevrolet")
MAKE = "toyota"

# Car model (e.g., "camry", "corolla", "civic", "f-150", "mustang")
# Leave as None to search all models for the make
MODEL = "camry"

# Year range (optional)
YEAR_MIN = 2018  # Minimum year (set to None for no minimum)
YEAR_MAX = 2023  # Maximum year (set to None for no maximum)

# Location settings
ZIP_CODE = "11230"  # ZIP code for search location
MAX_DISTANCE = 100  # Maximum distance in miles from ZIP code

# Stock type: "used", "new", or "cpo" (certified pre-owned)
STOCK_TYPE = "used"

# Price range (optional)
PRICE_MIN = None  # Minimum price (set to None for no minimum)
PRICE_MAX = None  # Maximum price (set to None for no maximum)

# Scraper settings
MAX_LISTINGS = 10  # Maximum number of listings to scrape
SHOW_BROWSER = True  # Set to True to see the browser in action
MAX_CONCURRENT = 3  # Number of listings to scrape in parallel

# Output directory
OUTPUT_DIR = "data"  # Base directory for saved listings

# ========================================


def build_search_url() -> str:
    """
    Build the cars.com search URL from the configuration above.

    Returns:
        Complete search URL with all filters
    """
    base_url = "https://www.cars.com/shopping/results/"

    # Build query parameters
    params = []

    # Stock type
    if STOCK_TYPE:
        params.append(f"stock_type={STOCK_TYPE}")

    # Make and model
    if MAKE:
        make_param = MAKE.lower().replace(" ", "-")
        params.append(f"makes[]={make_param}")

        if MODEL:
            model_param = f"{make_param}-{MODEL.lower().replace(' ', '-')}"
            params.append(f"models[]={model_param}")

    # Year range
    if YEAR_MIN:
        params.append(f"year_min={YEAR_MIN}")
    if YEAR_MAX:
        params.append(f"year_max={YEAR_MAX}")

    # Location
    if ZIP_CODE:
        params.append(f"zip={ZIP_CODE}")
    if MAX_DISTANCE:
        params.append(f"maximum_distance={MAX_DISTANCE}")

    # Price range
    if PRICE_MIN:
        params.append(f"price_min={PRICE_MIN}")
    if PRICE_MAX:
        params.append(f"price_max={PRICE_MAX}")

    # Combine URL and parameters
    if params:
        return f"{base_url}?{'&'.join(params)}"
    return base_url


async def main() -> None:
    """
    Main function to run the scraper with custom settings.

    Scrapes car listings and saves them in hierarchical folder structure.
    """
    print("=" * 60)
    print("🚗 Cars.com Scraper")
    print("=" * 60)

    # Display search parameters
    print("\n📋 Search Parameters:")
    print(f"  Make: {MAKE or 'Any'}")
    print(f"  Model: {MODEL or 'Any'}")
    if YEAR_MIN or YEAR_MAX:
        year_range = f"{YEAR_MIN or 'Any'} - {YEAR_MAX or 'Any'}"
        print(f"  Year: {year_range}")
    print(f"  Stock Type: {STOCK_TYPE or 'Any'}")
    print(f"  Location: {ZIP_CODE} (within {MAX_DISTANCE} miles)")
    if PRICE_MIN or PRICE_MAX:
        price_range = f"${PRICE_MIN or '0'} - ${PRICE_MAX or 'unlimited'}"
        print(f"  Price Range: {price_range}")
    print(f"  Max Listings: {MAX_LISTINGS}")

    # Build search URL
    search_url = build_search_url()
    print(f"\n🔗 Search URL:\n  {search_url}")

    # Configure scraper
    config = ScraperConfig(
        browser=BrowserConfig(
            headless=not SHOW_BROWSER,  # Show browser if SHOW_BROWSER is True
            slow_mo=100,  # Slight delay for human-like behavior
        ),
        max_concurrent_pages=MAX_CONCURRENT,
        min_delay_seconds=1.5,
        max_delay_seconds=3.0,
        max_retries=3,
        max_listings_per_page=MAX_LISTINGS,
    )

    print("\n⏳ Starting scraper...")
    print(f"{'🖥️  Browser visible' if SHOW_BROWSER else '🔇 Browser hidden (headless mode)'}\n")

    try:
        async with CarsScraper(config) as scraper:
            # Scrape listings
            listings = await scraper.scrape_search_page(search_url)

            print(f"\n{'=' * 60}")
            print(f"✅ Scraping Complete!")
            print(f"{'=' * 60}")
            print(f"\nFound {len(listings)} listings\n")

            if listings:
                # Display sample listings
                print("📝 Sample Listings:")
                for idx, listing in enumerate(listings[:3], 1):
                    print(f"\n  {idx}. {listing.year} {listing.make} {listing.model}")
                    if listing.price:
                        print(f"     💰 Price: ${listing.price:,}")
                    if listing.mileage:
                        print(f"     🛣️  Mileage: {listing.mileage:,} miles")
                    print(f"     📸 Images: {len(listing.images)}")
                    if listing.location:
                        print(f"     📍 Location: {listing.location}")

                if len(listings) > 3:
                    print(f"\n  ... and {len(listings) - 3} more listings")

                # Save in hierarchical structure
                print(f"\n{'=' * 60}")
                print("💾 Saving Results...")
                print(f"{'=' * 60}\n")

                await save_hierarchical(listings, base_dir=OUTPUT_DIR)

                # Show where files were saved
                print(f"\n{'=' * 60}")
                print("📁 Files Saved:")
                print(f"{'=' * 60}\n")

                print(f"Base directory: {OUTPUT_DIR}/\n")
                print("Structure:")
                for listing in listings[:5]:  # Show first 5
                    make_clean = listing.make.lower().replace(" ", "_")
                    model_clean = listing.model.lower().replace(" ", "_")
                    print(f"  {make_clean}/{model_clean}/{listing.listing_id}/")
                    print(f"    ├── listing.json")
                    print(f"    └── images/ ({len(listing.images)} images)")

                if len(listings) > 5:
                    print(f"\n  ... and {len(listings) - 5} more folders")

                # Summary statistics
                print(f"\n{'=' * 60}")
                print("📊 Summary:")
                print(f"{'=' * 60}\n")
                print(f"  Total listings: {len(listings)}")
                print(f"  Total images: {sum(len(l.images) for l in listings)}")

                prices = [float(l.price) for l in listings if l.price]
                if prices:
                    print(f"  Average price: ${sum(prices) / len(prices):,.2f}")
                    print(f"  Price range: ${min(prices):,.2f} - ${max(prices):,.2f}")

                mileages = [l.mileage for l in listings if l.mileage]
                if mileages:
                    print(f"  Average mileage: {sum(mileages) // len(mileages):,} miles")

                print(f"\n✅ All data saved to: {OUTPUT_DIR}/")
                print(f"\nℹ️  Each listing folder contains:")
                print(f"   • listing.json (year, description, price, specs, etc.)")
                print(f"   • images/ (all car photos)\n")

            else:
                print("❌ No listings found.")
                print("\n💡 Try:")
                print("  1. Adjusting the search parameters in main.py")
                print("  2. Setting SHOW_BROWSER = True to see what's happening")
                print("  3. Checking if the website structure has changed")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Set SHOW_BROWSER = True to debug")
        print("  3. Try reducing MAX_LISTINGS")
        raise


if __name__ == "__main__":
    print("\n" + "🏁 Starting..." + "\n")
    asyncio.run(main())
    print("\n" + "🏁 Done!" + "\n")
