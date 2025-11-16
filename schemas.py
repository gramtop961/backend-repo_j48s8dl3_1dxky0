"""
Database Schemas for Royer Exotics

Each Pydantic model corresponds to a MongoDB collection. Collection name is the lowercase of the class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Vehicle(BaseModel):
    """Vehicles available for rent"""
    slug: str = Field(..., description="URL-friendly unique identifier, e.g. 'lamborghini-huracan-evo'")
    make: str = Field(..., description="Brand, e.g. Lamborghini")
    model: str = Field(..., description="Model, e.g. Huracán EVO")
    year: int = Field(..., ge=1990, le=2100)
    category: str = Field(..., description="supercar | suv | executive | muscle")
    price_per_day: float = Field(..., ge=0)
    status: str = Field("available", description="available | booked | maintenance")
    horsepower: Optional[int] = Field(None, ge=0)
    zero_to_sixty: Optional[float] = Field(None, ge=0, description="0-60 mph in seconds")
    seats: Optional[int] = Field(None, ge=1, le=9)
    engine: Optional[str] = None
    thumbnails: List[HttpUrl] = Field(default_factory=list)
    gallery: List[HttpUrl] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    location: Optional[str] = Field("West Hollywood, CA")


class Testimonial(BaseModel):
    """Short client reviews and social proof"""
    name: str
    rating: float = Field(..., ge=0, le=5)
    comment: str
    avatar: Optional[HttpUrl] = None
    platform: Optional[str] = Field(None, description="Google, Instagram, Yelp, etc.")


class Booking(BaseModel):
    """Inbound booking inquiry"""
    vehicle_slug: Optional[str] = Field(None, description="Requested vehicle slug")
    full_name: str
    email: str
    phone: Optional[str] = None
    start_date: Optional[str] = Field(None, description="ISO date")
    end_date: Optional[str] = Field(None, description="ISO date")
    delivery: Optional[str] = Field(None, description="Pickup location or delivery address")
    notes: Optional[str] = None
    source: Optional[str] = Field("web", description="web | whatsapp | phone | instagram")
