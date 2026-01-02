"""
Unit tests for car listing models.

Tests Pydantic models for car listings, images, and validation rules.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models import CarCondition, CarImage, CarListing


class TestCarImage:
    """Tests for CarImage model."""

    def test_create_car_image(self) -> None:
        """Test creating a valid car image."""
        image = CarImage(url="https://example.com/image.jpg", is_primary=True, position=0)

        assert str(image.url) == "https://example.com/image.jpg"
        assert image.is_primary is True
        assert image.position == 0
        assert image.local_path is None

    def test_car_image_with_local_path(self) -> None:
        """Test car image with local file path."""
        image = CarImage(
            url="https://example.com/image.jpg",
            is_primary=False,
            position=1,
            local_path="/path/to/image.jpg",
        )

        assert image.local_path == "/path/to/image.jpg"

    def test_invalid_url(self) -> None:
        """Test that invalid URLs are rejected."""
        with pytest.raises(ValidationError):
            CarImage(url="not-a-url", position=0)


class TestCarListing:
    """Tests for CarListing model."""

    def test_create_minimal_listing(self) -> None:
        """Test creating a listing with minimal required fields."""
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="Toyota",
            model="Camry",
            year=2020,
            condition=CarCondition.USED,
        )

        assert listing.make == "Toyota"
        assert listing.model == "Camry"
        assert listing.year == 2020
        assert listing.condition == CarCondition.USED
        assert listing.price is None
        assert listing.mileage is None

    def test_create_complete_listing(self) -> None:
        """Test creating a listing with all fields populated."""
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="Honda",
            model="Civic",
            year=2021,
            condition=CarCondition.CERTIFIED,
            price=Decimal("25000.00"),
            mileage=15000,
            vin="1HGBH41JXMN109186",
            description="Excellent condition, one owner",
            location="Los Angeles, CA",
            dealer_name="ABC Motors",
            exterior_color="Blue",
            interior_color="Black",
            transmission="Automatic",
            drivetrain="FWD",
            fuel_type="Gasoline",
            mpg_city=30,
            mpg_highway=38,
            engine="2.0L 4-Cylinder",
        )

        assert listing.make == "Honda"
        assert listing.price == Decimal("25000.00")
        assert listing.mileage == 15000
        assert listing.vin == "1HGBH41JXMN109186"

    def test_add_image(self) -> None:
        """Test adding images to a listing."""
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="Ford",
            model="F-150",
            year=2022,
            condition=CarCondition.NEW,
        )

        # Add first image as primary
        listing.add_image("https://example.com/image1.jpg", is_primary=True)
        assert len(listing.images) == 1
        assert listing.images[0].is_primary is True
        assert listing.images[0].position == 0

        # Add second image
        listing.add_image("https://example.com/image2.jpg")
        assert len(listing.images) == 2
        assert listing.images[1].is_primary is False
        assert listing.images[1].position == 1

    def test_vin_validation(self) -> None:
        """Test VIN validation rules."""
        # Valid VIN
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="Tesla",
            model="Model 3",
            year=2023,
            condition=CarCondition.NEW,
            vin="5YJ3E1EA1KF000001",
        )
        assert listing.vin == "5YJ3E1EA1KF000001"

        # VIN with invalid characters (I, O, Q)
        with pytest.raises(ValidationError, match="VIN cannot contain"):
            CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="Tesla",
                model="Model 3",
                year=2023,
                condition=CarCondition.NEW,
                vin="5YJ3E1EAIKF00000I",  # Contains 'I'
            )

    def test_vin_uppercase_conversion(self) -> None:
        """Test that VIN is converted to uppercase."""
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="BMW",
            model="X5",
            year=2022,
            condition=CarCondition.USED,
            vin="wba5a5c51ed000000",  # Lowercase
        )
        assert listing.vin == "WBA5A5C51ED000000"  # Should be uppercase

    def test_invalid_year(self) -> None:
        """Test that invalid years are rejected."""
        with pytest.raises(ValidationError):
            CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="DeLorean",
                model="DMC-12",
                year=1885,  # Too old
                condition=CarCondition.USED,
            )

        with pytest.raises(ValidationError):
            CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="Future",
                model="Car",
                year=2050,  # Too far in future
                condition=CarCondition.NEW,
            )

    def test_negative_price(self) -> None:
        """Test that negative prices are rejected."""
        with pytest.raises(ValidationError):
            CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="Toyota",
                model="Corolla",
                year=2020,
                condition=CarCondition.USED,
                price=Decimal("-1000.00"),  # Negative price
            )

    def test_negative_mileage(self) -> None:
        """Test that negative mileage is rejected."""
        with pytest.raises(ValidationError):
            CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="Honda",
                model="Accord",
                year=2019,
                condition=CarCondition.USED,
                mileage=-5000,  # Negative mileage
            )

    def test_model_serialization(self) -> None:
        """Test that model can be serialized to dict/JSON."""
        listing = CarListing(
            url="https://www.cars.com/vehicledetail/12345",
            make="Mazda",
            model="CX-5",
            year=2021,
            condition=CarCondition.USED,
            price=Decimal("28000.50"),
        )

        # Serialize to dict
        data = listing.model_dump()
        assert data["make"] == "Mazda"
        assert data["condition"] == "used"

        # Serialize to JSON-compatible dict
        json_data = listing.model_dump(mode="json")
        assert isinstance(json_data["price"], str)  # Decimal as string
        assert json_data["scraped_at"]  # DateTime serialized


class TestCarCondition:
    """Tests for CarCondition enum."""

    def test_condition_values(self) -> None:
        """Test that CarCondition enum has expected values."""
        assert CarCondition.NEW == "new"
        assert CarCondition.USED == "used"
        assert CarCondition.CERTIFIED == "certified"

    def test_condition_in_listing(self) -> None:
        """Test using different condition values in listing."""
        for condition in [CarCondition.NEW, CarCondition.USED, CarCondition.CERTIFIED]:
            listing = CarListing(
                url="https://www.cars.com/vehicledetail/12345",
                make="Test",
                model="Car",
                year=2020,
                condition=condition,
            )
            assert listing.condition == condition
