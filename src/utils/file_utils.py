"""
File I/O utilities for saving and loading scraped data.

Provides functions to export car listings to JSON and CSV formats.
"""

import csv
import json
from pathlib import Path
from typing import Any

import aiofiles

from src.models import CarListing


async def save_to_json(listings: list[CarListing], filepath: str) -> None:
    """
    Save car listings to a JSON file asynchronously.

    Args:
        listings: List of CarListing objects to save
        filepath: Path to the output JSON file
    """
    # Convert listings to dicts
    data = [listing.model_dump(mode="json") for listing in listings]

    # Ensure parent directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Write to file asynchronously
    async with aiofiles.open(filepath, mode="w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"Saved {len(listings)} listings to {filepath}")


async def load_from_json(filepath: str) -> list[CarListing]:
    """
    Load car listings from a JSON file asynchronously.

    Args:
        filepath: Path to the JSON file

    Returns:
        List of CarListing objects
    """
    async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)

    listings = [CarListing(**item) for item in data]
    print(f"Loaded {len(listings)} listings from {filepath}")
    return listings


def save_to_csv(listings: list[CarListing], filepath: str) -> None:
    """
    Save car listings to a CSV file.

    Args:
        listings: List of CarListing objects to save
        filepath: Path to the output CSV file
    """
    if not listings:
        print("No listings to save")
        return

    # Ensure parent directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Define CSV columns
    fieldnames = [
        "listing_id",
        "url",
        "make",
        "model",
        "year",
        "condition",
        "price",
        "mileage",
        "vin",
        "location",
        "dealer_name",
        "exterior_color",
        "interior_color",
        "transmission",
        "drivetrain",
        "fuel_type",
        "mpg_city",
        "mpg_highway",
        "engine",
        "image_count",
        "scraped_at",
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for listing in listings:
            row: dict[str, Any] = {
                "listing_id": str(listing.listing_id),
                "url": str(listing.url),
                "make": listing.make,
                "model": listing.model,
                "year": listing.year,
                "condition": listing.condition,
                "price": str(listing.price) if listing.price else "",
                "mileage": listing.mileage,
                "vin": listing.vin,
                "location": listing.location,
                "dealer_name": listing.dealer_name,
                "exterior_color": listing.exterior_color,
                "interior_color": listing.interior_color,
                "transmission": listing.transmission,
                "drivetrain": listing.drivetrain,
                "fuel_type": listing.fuel_type,
                "mpg_city": listing.mpg_city,
                "mpg_highway": listing.mpg_highway,
                "engine": listing.engine,
                "image_count": len(listing.images),
                "scraped_at": listing.scraped_at.isoformat(),
            }
            writer.writerow(row)

    print(f"Saved {len(listings)} listings to {filepath}")


async def save_hierarchical(listings: list[CarListing], base_dir: str = "data") -> None:
    """
    Save car listings in hierarchical folder structure: make/model/listing_id/.

    Structure:
        base_dir/
            {make}/
                {model}/
                    {listing_id}/
                        listing.json
                        images/
                            image_00.jpg
                            image_01.jpg

    Args:
        listings: List of CarListing objects to save
        base_dir: Base directory for the hierarchical structure
    """
    import httpx

    if not listings:
        print("No listings to save")
        return

    base_path = Path(base_dir)
    saved_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for listing in listings:
            # Create directory structure: make/model/listing_id
            make_clean = listing.make.lower().replace(" ", "_")
            model_clean = listing.model.lower().replace(" ", "_")
            listing_dir = base_path / make_clean / model_clean / str(listing.listing_id)
            listing_dir.mkdir(parents=True, exist_ok=True)

            # Save listing details to JSON
            listing_file = listing_dir / "listing.json"
            listing_data = listing.model_dump(mode="json")

            async with aiofiles.open(listing_file, mode="w", encoding="utf-8") as f:
                await f.write(json.dumps(listing_data, indent=2, ensure_ascii=False))

            # Download and save images
            if listing.images:
                images_dir = listing_dir / "images"
                images_dir.mkdir(exist_ok=True)

                for idx, image in enumerate(listing.images):
                    try:
                        response = await client.get(str(image.url))
                        response.raise_for_status()

                        # Determine file extension
                        extension = _get_image_extension(
                            str(image.url), response.headers.get("content-type", "")
                        )
                        filename = f"image_{idx:02d}{extension}"
                        image_path = images_dir / filename

                        # Save image
                        image_path.write_bytes(response.content)

                        # Update image model with local path
                        image.local_path = str(image_path)

                    except Exception as e:
                        print(f"Failed to download image {image.url}: {e}")

            saved_count += 1
            print(
                f"Saved {listing.year} {listing.make} {listing.model} "
                f"to {listing_dir.relative_to(base_path)}"
            )

    print(f"\n✅ Saved {saved_count} listings to {base_dir}/")
    print(f"📁 Structure: {base_dir}/{{make}}/{{model}}/{{listing_id}}/")


def _get_image_extension(url: str, content_type: str) -> str:
    """
    Determine image file extension from URL or content-type.

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
