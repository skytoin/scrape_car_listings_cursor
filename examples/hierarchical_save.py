"""
Hierarchical saving example for the cars.com scraper.

This script demonstrates how to save car listings in an organized
folder structure: make/model/listing_id/
"""

import asyncio

from src.models import BrowserConfig, ScraperConfig
from src.scraper import CarsScraper
from src.utils import save_hierarchical


async def main() -> None:
    """
    Scrape car listings and save in hierarchical folder structure.

    Folder structure:
        data/
            toyota/
                camry/
                    {listing_id}/
                        listing.json
                        images/
                            image_00.jpg
                            image_01.jpg
                avalon/
                    {listing_id}/
                        listing.json
                        images/
            bmw/
                x5/
                    {listing_id}/
                        listing.json
                        images/
    """
    print("=== Cars.com Hierarchical Scraper ===\n")

    # Configure the scraper
    config = ScraperConfig(
        browser=BrowserConfig(
            headless=False,  # Set to True to run without GUI
            slow_mo=100,
        ),
        max_concurrent_pages=2,  # Scrape 2 listings in parallel
        min_delay_seconds=2.0,
        max_delay_seconds=4.0,
        max_retries=3,
        save_images=False,  # Images will be downloaded by save_hierarchical
        max_listings_per_page=5,  # Limit to 5 listings for demo
    )

    # Example search URL - Toyota Camry in Los Angeles
    search_url = (
        "https://www.cars.com/shopping/results/"
        "?stock_type=used&makes[]=toyota&models[]=toyota-camry"
        "&zip=90001&maximum_distance=100"
    )

    print(f"Search URL: {search_url}\n")
    print("Starting scraper...\n")

    async with CarsScraper(config) as scraper:
        # Scrape all listings from the search page
        listings = await scraper.scrape_search_page(search_url)

        print(f"\n=== Scraping Complete ===")
        print(f"Successfully scraped {len(listings)} listings\n")

        if listings:
            # Display sample data
            print("=== Sample Listings ===")
            for idx, listing in enumerate(listings[:3], 1):
                print(f"\n{idx}. {listing.year} {listing.make} {listing.model}")
                print(f"   Price: ${listing.price}" if listing.price else "   Price: N/A")
                print(
                    f"   Mileage: {listing.mileage:,} miles"
                    if listing.mileage
                    else "   Mileage: N/A"
                )
                print(f"   Images: {len(listing.images)}")

            # Save in hierarchical structure
            print("\n=== Saving to Hierarchical Structure ===")
            await save_hierarchical(listings, base_dir="data")

            print("\n=== Directory Structure Created ===")
            print("data/")
            for listing in listings:
                make_clean = listing.make.lower().replace(" ", "_")
                model_clean = listing.model.lower().replace(" ", "_")
                print(f"  └── {make_clean}/")
                print(f"      └── {model_clean}/")
                print(f"          └── {listing.listing_id}/")
                print(f"              ├── listing.json")
                if listing.images:
                    print(f"              └── images/")
                    print(f"                  ├── image_00.jpg")
                    if len(listing.images) > 1:
                        print(f"                  ├── ...")
                        print(f"                  └── image_{len(listing.images) - 1:02d}.jpg")
                print()

        else:
            print("No listings found. The page structure may have changed.")
            print("Try running with headless=False to see what's happening.")


async def scrape_multiple_makes() -> None:
    """
    Example of scraping multiple car makes to see hierarchical structure.

    This will create folders for different makes and models.
    """
    print("=== Multi-Make Hierarchical Scraper ===\n")

    config = ScraperConfig(
        browser=BrowserConfig(headless=True),
        max_concurrent_pages=3,
        max_listings_per_page=3,  # Just 3 per search for demo
    )

    all_listings = []

    # Search for different makes
    searches = [
        ("Toyota Camry", "?stock_type=used&makes[]=toyota&models[]=toyota-camry"),
        ("Honda Civic", "?stock_type=used&makes[]=honda&models[]=honda-civic"),
        ("BMW X5", "?stock_type=used&makes[]=bmw&models[]=bmw-x5"),
    ]

    async with CarsScraper(config) as scraper:
        for name, query in searches:
            print(f"Scraping {name}...")
            url = f"https://www.cars.com/shopping/results/{query}"
            listings = await scraper.scrape_search_page(url)
            all_listings.extend(listings)
            print(f"  Found {len(listings)} listings\n")

        if all_listings:
            print(f"=== Total: {len(all_listings)} listings ===\n")
            await save_hierarchical(all_listings, base_dir="data")

            # Show unique makes and models
            makes = set(f"{l.make}/{l.model}" for l in all_listings)
            print("\n=== Makes/Models Saved ===")
            for make_model in sorted(makes):
                print(f"  • {make_model}")


if __name__ == "__main__":
    # Run the main hierarchical save demo
    asyncio.run(main())

    # Uncomment to scrape multiple makes:
    # asyncio.run(scrape_multiple_makes())
