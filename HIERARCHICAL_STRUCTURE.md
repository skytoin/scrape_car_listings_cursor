# 📁 Hierarchical Folder Structure Guide

This guide explains how to save car listings in an organized hierarchical structure.

## 🎯 Structure Overview

```
data/
├── toyota/
│   ├── camry/
│   │   ├── uuid-12345/
│   │   │   ├── listing.json          # All car details
│   │   │   └── images/
│   │   │       ├── image_00.jpg      # Primary image
│   │   │       ├── image_01.jpg
│   │   │       └── image_02.jpg
│   │   └── uuid-67890/
│   │       ├── listing.json
│   │       └── images/
│   │           └── image_00.jpg
│   └── avalon/
│       └── uuid-abcde/
│           ├── listing.json
│           └── images/
├── bmw/
│   └── x5/
│       └── uuid-fghij/
│           ├── listing.json
│           └── images/
└── honda/
    └── civic/
        └── uuid-klmno/
            ├── listing.json
            └── images/
```

## 🔧 How to Use

### Quick Example

```python
import asyncio
from src.scraper import CarsScraper
from src.utils import save_hierarchical

async def main():
    async with CarsScraper() as scraper:
        listings = await scraper.scrape_search_page(search_url)

        # Save in hierarchical structure
        await save_hierarchical(listings, base_dir="data")

asyncio.run(main())
```

### Full Example

```python
import asyncio
from src.models import ScraperConfig, BrowserConfig
from src.scraper import CarsScraper
from src.utils import save_hierarchical

async def main():
    config = ScraperConfig(
        browser=BrowserConfig(headless=True),
        max_concurrent_pages=3,
    )

    search_url = (
        "https://www.cars.com/shopping/results/"
        "?stock_type=used&makes[]=toyota&models[]=toyota-camry"
    )

    async with CarsScraper(config) as scraper:
        listings = await scraper.scrape_search_page(search_url)

        # Save to custom directory
        await save_hierarchical(listings, base_dir="my_cars")

asyncio.run(main())
```

## 📄 listing.json Contents

Each `listing.json` file contains complete car details:

```json
{
  "listing_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://www.cars.com/vehicledetail/detail/...",
  "make": "Toyota",
  "model": "Camry",
  "year": 2020,
  "condition": "used",
  "price": "25000.00",
  "mileage": 15000,
  "vin": "1HGBH41JXMN109186",
  "description": "Excellent condition, one owner vehicle...",
  "location": "Los Angeles, CA",
  "dealer_name": "ABC Motors",
  "exterior_color": "Blue",
  "interior_color": "Black",
  "transmission": "Automatic",
  "drivetrain": "FWD",
  "fuel_type": "Gasoline",
  "mpg_city": 30,
  "mpg_highway": 38,
  "engine": "2.0L 4-Cylinder",
  "images": [
    {
      "image_id": "img-uuid-1",
      "url": "https://example.com/original-image-url.jpg",
      "local_path": "data/toyota/camry/uuid-12345/images/image_00.jpg",
      "is_primary": true,
      "position": 0
    }
  ],
  "scraped_at": "2025-01-02T12:34:56.789Z"
}
```

## 🖼️ Images

- **Automatically downloaded** when using `save_hierarchical()`
- Saved in `images/` subdirectory within each listing folder
- Named as `image_00.jpg`, `image_01.jpg`, etc.
- `image_00.jpg` is always the primary/featured image
- File extensions determined from actual image type (.jpg, .png, .webp)

## 🔍 Finding Specific Cars

### By Make
```bash
ls data/toyota/
# camry avalon corolla
```

### By Model
```bash
ls data/toyota/camry/
# uuid-12345 uuid-67890 uuid-abcde
```

### View Listing Details
```bash
cat data/toyota/camry/uuid-12345/listing.json
```

### View Images
```bash
ls data/toyota/camry/uuid-12345/images/
# image_00.jpg image_01.jpg image_02.jpg
```

## 🛠️ Customization

### Custom Base Directory

```python
await save_hierarchical(listings, base_dir="my_custom_folder")
```

Result:
```
my_custom_folder/
├── toyota/
│   └── camry/
```

### Processing Listings

```python
from pathlib import Path
import json

# Load a specific listing
listing_path = Path("data/toyota/camry/uuid-12345/listing.json")
with open(listing_path) as f:
    car_data = json.load(f)

print(f"Price: ${car_data['price']}")
print(f"Mileage: {car_data['mileage']:,} miles")
```

### Find All Listings for a Make/Model

```python
from pathlib import Path

# Find all Toyota Camry listings
camry_dir = Path("data/toyota/camry")
for listing_dir in camry_dir.iterdir():
    listing_file = listing_dir / "listing.json"
    if listing_file.exists():
        print(f"Found listing: {listing_dir.name}")
```

## 📊 Benefits of Hierarchical Structure

✅ **Easy browsing** - Navigate by make and model
✅ **Organized images** - Each car's images in its own folder
✅ **Self-contained** - Each listing folder has everything
✅ **Scalable** - Works great with thousands of listings
✅ **Human-readable** - Easy to understand folder structure
✅ **Programmatic access** - Simple to process with scripts

## 🚀 Run the Example

```bash
python examples/hierarchical_save.py
```

This will scrape Toyota Camry listings and organize them in the hierarchical structure!

## 💡 Tips

- **Folder names** are lowercase with underscores (e.g., "toyota_highlander")
- **Special characters** in make/model names are replaced with underscores
- **UUID folders** prevent conflicts if scraping the same car multiple times
- **Images** are only downloaded once per listing (not re-downloaded if already exists)
- **JSON files** are human-readable and can be edited if needed
