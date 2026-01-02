# 🚗 Cars.com Scraper

A **modern, scalable Python scraper** for extracting car listings from [Cars.com](https://www.cars.com/). Built with **Playwright** for browser automation, **Pydantic V2** for data validation, and **asyncio** for high-performance parallel scraping.

## ✨ Features

- 🚀 **Parallel Scraping** - Scrape multiple listings concurrently for maximum speed
- 🎭 **Anti-Detection** - Behaves like a real browser with randomized delays and mouse movements
- 📸 **Image Download** - Automatically download and save car images locally
- ✅ **Data Validation** - Type-safe models with Pydantic V2
- 📊 **Multiple Export Formats** - Save results as JSON or CSV
- 🔄 **Retry Logic** - Automatic retry with exponential backoff for failed requests
- ⚙️ **Highly Configurable** - Customize browser behavior, rate limiting, and more

## 📋 Data Extracted

Each scraped listing includes:

- **Basic Info**: Make, model, year, condition (new/used/certified)
- **Pricing**: Listed price, mileage
- **Details**: VIN, exterior/interior color, transmission, drivetrain
- **Performance**: Fuel type, MPG (city/highway), engine
- **Location**: Dealer name and location
- **Media**: Multiple high-quality images with URLs
- **Description**: Full listing description text

## 🛠️ Installation

### Prerequisites

- Python 3.11 or higher
- UV package manager (recommended) or pip

### Setup with UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/skytoin/scrape_car_listings_claude.git
cd scrape_car_listings_claude

# Sync dependencies
uv sync

# Install Playwright browsers
python -m playwright install chromium
```

### Setup with pip

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install playwright pydantic httpx pillow fake-useragent aiofiles

# Install Playwright browsers
python -m playwright install chromium
```

## 🚀 Quick Start

```python
import asyncio
from src.models import ScraperConfig, BrowserConfig
from src.scraper import CarsScraper
from src.utils import save_to_json, save_to_csv

async def main():
    # Configure the scraper
    config = ScraperConfig(
        browser=BrowserConfig(
            headless=True,  # Run without GUI
            slow_mo=100,    # Human-like delays
        ),
        max_concurrent_pages=3,
        save_images=True,
    )

    # Search for used Toyota Camry
    search_url = (
        "https://www.cars.com/shopping/results/"
        "?stock_type=used&makes[]=toyota&models[]=toyota-camry"
    )

    async with CarsScraper(config) as scraper:
        listings = await scraper.scrape_search_page(search_url)

        # Save results
        await save_to_json(listings, "output/listings.json")
        save_to_csv(listings, "output/listings.csv")

        print(f"Scraped {len(listings)} listings!")

asyncio.run(main())
```

## 📖 Usage Examples

### Basic Search Scraping

```python
# See examples/basic_usage.py
python examples/basic_usage.py
```

### Hierarchical Folder Structure (Recommended)

Save listings organized by make/model:

```python
from src.utils import save_hierarchical

async with CarsScraper() as scraper:
    listings = await scraper.scrape_search_page(search_url)

    # Save in organized folder structure: make/model/listing_id/
    await save_hierarchical(listings, base_dir="data")

# Creates:
# data/
#   toyota/
#     camry/
#       {listing_id}/
#         listing.json (all details)
#         images/
#           image_00.jpg
#           image_01.jpg
```

See [HIERARCHICAL_STRUCTURE.md](HIERARCHICAL_STRUCTURE.md) for complete guide.

### Scrape a Single Listing

```python
async with CarsScraper() as scraper:
    listing = await scraper.scrape_listing(
        "https://www.cars.com/vehicledetail/..."
    )
```

### Multi-Page Scraping

```python
async with CarsScraper(config) as scraper:
    all_listings = []
    for page in range(1, 4):
        url = f"{base_url}&page={page}"
        listings = await scraper.scrape_search_page(url)
        all_listings.extend(listings)
```

### Custom Configuration

```python
config = ScraperConfig(
    browser=BrowserConfig(
        headless=False,          # Show browser window
        viewport_width=1920,
        viewport_height=1080,
        timeout=30000,           # 30 second timeout
    ),
    max_concurrent_pages=5,      # Scrape 5 pages at once
    min_delay_seconds=2.0,       # Minimum delay between requests
    max_delay_seconds=4.0,       # Maximum delay
    max_retries=3,               # Retry failed requests
    save_images=True,            # Download images
    image_directory="./images",
    max_listings_per_page=25,    # Max listings per search page
)
```

## 📁 Project Structure

```
.
├── src/
│   ├── models/              # Pydantic data models
│   │   ├── car_listing.py   # CarListing, CarImage models
│   │   └── scraper_config.py  # Configuration models
│   ├── scraper/             # Core scraping logic
│   │   ├── browser_manager.py  # Browser automation
│   │   ├── listing_extractor.py  # Data extraction
│   │   └── cars_scraper.py      # Main scraper orchestrator
│   └── utils/               # Utility functions
│       └── file_utils.py    # JSON/CSV export
├── examples/
│   └── basic_usage.py       # Usage examples
├── tests/                   # Unit tests
├── pyproject.toml           # Project configuration
└── CLAUDE.md                # Development guidelines
```

## ⚙️ Configuration Reference

### BrowserConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | bool | True | Run browser in headless mode |
| `user_agent` | str\|None | None | Custom user agent (random if None) |
| `viewport_width` | int | 1920 | Browser viewport width |
| `viewport_height` | int | 1080 | Browser viewport height |
| `timeout` | int | 30000 | Default timeout in milliseconds |
| `slow_mo` | int | 100 | Delay between actions (ms) |

### ScraperConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_concurrent_pages` | int | 3 | Max parallel scraping tasks |
| `min_delay_seconds` | float | 1.0 | Min delay between requests |
| `max_delay_seconds` | float | 3.0 | Max delay between requests |
| `max_retries` | int | 3 | Retry attempts for failures |
| `save_images` | bool | False | Download images locally |
| `image_directory` | str | "./images" | Image save directory |
| `max_listings_per_page` | int | 25 | Max listings per search page |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest src/models/tests/test_car_listing.py -v
```

## 🤝 Contributing

Contributions are welcome! Please see [CLAUDE.md](CLAUDE.md) for development guidelines.

## 📄 License

MIT License - feel free to use this project for any purpose.

## ⚠️ Disclaimer

This scraper is for educational purposes only. Always respect websites' Terms of Service and robots.txt. Be responsible with scraping frequency and don't overload servers.

## 🛣️ Roadmap

- [ ] Support for more car listing sites (AutoTrader, CarGurus)
- [ ] Price tracking and alerts
- [ ] Advanced filtering (price range, location, features)
- [ ] Database integration (SQLite, PostgreSQL)
- [ ] Web dashboard for results visualization
- [ ] API server mode

## 📘 Development

For detailed development guidelines including code style, architecture, testing practices, and Git workflow, see [CLAUDE.md](CLAUDE.md).