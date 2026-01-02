"""
Scraper configuration models.

Defines configuration for browser automation, rate limiting,
and anti-detection measures.
"""

from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    """
    Browser automation configuration.

    Attributes:
        headless: Run browser in headless mode
        user_agent: Custom user agent string (None = use default)
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        timeout: Default timeout for page operations in milliseconds
        slow_mo: Delay between actions in milliseconds (for human-like behavior)
    """

    headless: bool = True
    user_agent: str | None = None
    viewport_width: int = Field(default=1920, ge=800)
    viewport_height: int = Field(default=1080, ge=600)
    timeout: int = Field(default=30000, ge=1000)
    slow_mo: int = Field(default=100, ge=0, le=5000)

    model_config = {"use_enum_values": True, "populate_by_name": True}


class ScraperConfig(BaseModel):
    """
    Complete scraper configuration.

    Attributes:
        browser: Browser automation settings
        max_concurrent_pages: Maximum number of pages to scrape concurrently
        min_delay_seconds: Minimum delay between requests in seconds
        max_delay_seconds: Maximum delay between requests in seconds
        max_retries: Maximum number of retries for failed requests
        save_images: Whether to download and save images locally
        image_directory: Directory to save downloaded images
        max_listings_per_page: Maximum listings to extract from each page
    """

    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    max_concurrent_pages: int = Field(default=3, ge=1, le=10)
    min_delay_seconds: float = Field(default=1.0, ge=0.1)
    max_delay_seconds: float = Field(default=3.0, ge=0.1)
    max_retries: int = Field(default=3, ge=0, le=10)
    save_images: bool = False
    image_directory: str = "./images"
    max_listings_per_page: int = Field(default=25, ge=1)

    model_config = {"use_enum_values": True, "populate_by_name": True}
