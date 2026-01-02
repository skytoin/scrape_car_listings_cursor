"""
Car listing data models.

Defines the structure for car listings scraped from cars.com,
including images, metadata, and validation rules.
"""

from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CarCondition(str, Enum):
    """Enumeration of possible car conditions."""

    NEW = "new"
    USED = "used"
    CERTIFIED = "certified"


class CarImage(BaseModel):
    """
    Model for car images.

    Attributes:
        image_id: Unique identifier for the image
        url: Original URL of the image
        local_path: Optional local file path if image is downloaded
        is_primary: Whether this is the main listing image
        position: Order position in the image gallery
    """

    image_id: UUID = Field(default_factory=uuid4)
    url: HttpUrl
    local_path: Optional[str] = None
    is_primary: bool = False
    position: int = Field(ge=0)

    model_config = {"use_enum_values": True, "populate_by_name": True}


class CarListing(BaseModel):
    """
    Complete car listing model.

    Attributes:
        listing_id: Unique identifier for the listing
        url: URL of the listing page
        make: Car manufacturer (e.g., Toyota, Honda)
        model: Car model name (e.g., Camry, Civic)
        year: Year the car was produced
        condition: New, used, or certified pre-owned
        price: Listed price in USD
        mileage: Current mileage (None for new cars)
        vin: Vehicle Identification Number
        description: Full text description from the listing
        images: List of car images
        location: City and state of the listing
        dealer_name: Name of the selling dealership
        exterior_color: Exterior paint color
        interior_color: Interior color
        transmission: Type of transmission
        drivetrain: Drivetrain type (FWD, RWD, AWD, 4WD)
        fuel_type: Type of fuel (Gas, Diesel, Electric, Hybrid)
        mpg_city: City fuel economy (MPG)
        mpg_highway: Highway fuel economy (MPG)
        engine: Engine description
        scraped_at: Timestamp when listing was scraped
    """

    listing_id: UUID = Field(default_factory=uuid4)
    url: HttpUrl
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1900, le=2030)
    condition: CarCondition
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    mileage: Optional[int] = Field(None, ge=0)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    description: Optional[str] = None
    images: list[CarImage] = []
    location: Optional[str] = None
    dealer_name: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    fuel_type: Optional[str] = None
    mpg_city: Optional[int] = Field(None, ge=0)
    mpg_highway: Optional[int] = Field(None, ge=0)
    engine: Optional[str] = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate VIN format.

        Args:
            v: VIN string to validate

        Returns:
            Uppercased VIN string

        Raises:
            ValueError: If VIN contains invalid characters
        """
        if v is None:
            return v

        # VIN should not contain I, O, or Q
        invalid_chars = set("IOQ")
        if any(char in invalid_chars for char in v.upper()):
            raise ValueError("VIN cannot contain letters I, O, or Q")

        return v.upper()

    def add_image(
        self, url: str, is_primary: bool = False, local_path: Optional[str] = None
    ) -> None:
        """
        Add an image to the listing.

        Args:
            url: URL of the image
            is_primary: Whether this is the primary image
            local_path: Optional local file path for downloaded image
        """
        position = len(self.images)
        image = CarImage(url=url, is_primary=is_primary, local_path=local_path, position=position)
        self.images.append(image)

    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,
    }
