"""
Basic usage example for the cars.com scraper.

This script demonstrates how to scrape car listings from a search page,
extract data, and save results to JSON and CSV files.
"""

import asyncio

from src.models import BrowserConfig, ScraperConfig
from src.scraper import CarsScraper
from src.utils import save_to_csv, save_to_json


async def main() -> None:
    """
    Main function demonstrating scraper usage.

    Scrapes listings from a cars.com search page and saves results.
    """
    print("=== Cars.com Scraper Demo ===\n")

    # Configure the scraper
    config = ScraperConfig(
        browser=BrowserConfig(
            headless=False,  # Set to True to run without GUI
            slow_mo=100,  # Delay between actions (ms) for human-like behavior
        ),
        max_concurrent_pages=2,  # Scrape 2 listings in parallel
        min_delay_seconds=1.5,  # Minimum delay between requests
        max_delay_seconds=3.0,  # Maximum delay between requests
        max_retries=3,  # Retry failed requests up to 3 times
        save_images=False,  # Set to True to download images locally
        image_directory="./images",  # Directory for saved images
        max_listings_per_page=5,  # Limit to first 5 listings (for demo)
    )

    # Example search URL - modify this to your desired search
    # This searches for used Toyota Camry in Los Angeles
    search_url = (
        "https://www.cars.com/shopping/results/"
        "?stock_type=used&makes[]=toyota&models[]=toyota-camry"
        "&zip=90001&list_price_max=&maximum_distance=100"
    )

    print(f"Search URL: {search_url}\n")

    # Use context manager for automatic cleanup
    async with CarsScraper(config) as scraper:
        print("Starting scraper...\n")

        # Scrape all listings from the search page
        listings = await scraper.scrape_search_page(search_url)

        print(f"\n=== Scraping Complete ===")
        print(f"Successfully scraped {len(listings)} listings\n")

        if listings:
            # Display sample data
            print("=== Sample Listing ===")
            sample = listings[0]
            print(f"Make/Model: {sample.year} {sample.make} {sample.model}")
            print(f"Price: ${sample.price}" if sample.price else "Price: N/A")
            print(f"Mileage: {sample.mileage:,} miles" if sample.mileage else "Mileage: N/A")
            print(f"Condition: {sample.condition}")
            print(f"Location: {sample.location}")
            print(f"Images: {len(sample.images)}")
            print(f"URL: {sample.url}\n")

            # Save results
            print("=== Saving Results ===")
            await save_to_json(listings, "output/listings.json")
            save_to_csv(listings, "output/listings.csv")

            # For hierarchical save (make/model/listing_id/), see:
            # examples/hierarchical_save.py or use:
            # from src.utils import save_hierarchical
            # await save_hierarchical(listings, base_dir="data")

            print("\n=== Summary ===")
            print(f"Total listings: {len(listings)}")
            print(f"Total images: {sum(len(l.images) for l in listings)}")
            print(
                f"Average price: ${sum(float(l.price or 0) for l in listings) / len(listings):.2f}"
            )

        else:
            print("No listings found. The page structure may have changed.")
            print("Try running with headless=False to see what's happening.")


async def scrape_single_listing() -> None:
    """
    Example of scraping a single listing by URL.

    Useful when you already have specific listing URLs.
    """
    print("=== Single Listing Scraper Demo ===\n")

    # Replace with an actual listing URL from cars.com
    listing_url = "https://www.cars.com/vehicledetail/EXAMPLE_ID/"

    config = ScraperConfig(
        browser=BrowserConfig(headless=False),
        save_images=True,  # Download images for this listing
    )

    async with CarsScraper(config) as scraper:
        print(f"Scraping: {listing_url}\n")

        listing = await scraper.scrape_listing(listing_url)

        if listing:
            print("=== Listing Details ===")
            print(f"Vehicle: {listing.year} {listing.make} {listing.model}")
            print(f"Price: ${listing.price}" if listing.price else "Price: N/A")
            print(f"VIN: {listing.vin}")
            print(f"Images downloaded: {len(listing.images)}")

            # Save single listing
            await save_to_json([listing], "output/single_listing.json")
        else:
            print("Failed to scrape listing")


async def scrape_multiple_pages() -> None:
    """
    Example of scraping multiple search result pages.

    Demonstrates how to iterate through pagination.
    """
    print("=== Multi-Page Scraper Demo ===\n")

    # Base search URL
    base_url = "https://www.cars.com/shopping/results/?stock_type=used&makes[]=honda"

    config = ScraperConfig(
        max_concurrent_pages=3,
        max_listings_per_page=10,  # Scrape up to 10 per page
    )

    all_listings = []

    async with CarsScraper(config) as scraper:
        # Scrape first 3 pages
        for page_num in range(1, 4):
            page_url = f"{base_url}&page={page_num}"
            print(f"Scraping page {page_num}...")

            listings = await scraper.scrape_search_page(page_url)
            all_listings.extend(listings)

            print(f"Found {len(listings)} listings on page {page_num}")

        print(f"\n=== Total: {len(all_listings)} listings ===")

        # Save all results
        if all_listings:
            await save_to_json(all_listings, "output/multi_page_listings.json")
            save_to_csv(all_listings, "output/multi_page_listings.csv")


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(main())

    # Uncomment to run other examples:
    # asyncio.run(scrape_single_listing())
    # asyncio.run(scrape_multiple_pages())
