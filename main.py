import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import db, create_document, get_documents
from schemas import Vehicle, Testimonial, Booking

app = FastAPI(title="Royer Exotics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "Royer Exotics API", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Seed endpoint to insert a few vehicles and testimonials (idempotent)
@app.post("/seed")
def seed_data():
    sample_cars = [
        Vehicle(
            slug="lamborghini-huracan-evo",
            make="Lamborghini",
            model="Huracán EVO",
            year=2021,
            category="supercar",
            price_per_day=1299,
            status="available",
            horsepower=631,
            zero_to_sixty=2.9,
            seats=2,
            engine="V10",
            thumbnails=[
                # Realistic Huracán photos (studio/night)
                "https://images.unsplash.com/photo-1504215680853-026ed2a45def?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1621135802920-133df287f89d?q=80&w=1920&auto=format&fit=crop",
            ],
            gallery=[
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?q=80&w=1920&auto=format&fit=crop",
            ],
            features=["Apple CarPlay", "Carbon Ceramic Brakes", "GPS Tracking"],
        ),
        Vehicle(
            slug="rolls-royce-cullinan",
            make="Rolls-Royce",
            model="Cullinan",
            year=2022,
            category="suv",
            price_per_day=1499,
            status="available",
            horsepower=563,
            zero_to_sixty=4.9,
            seats=5,
            engine="V12",
            thumbnails=[
                "https://images.unsplash.com/photo-1619767886558-efdc259cde1f?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=1920&auto=format&fit=crop",
            ],
            gallery=[
                "https://images.unsplash.com/photo-1549924231-f129b911e442?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?q=80&w=1920&auto=format&fit=crop",
            ],
            features=["Rear-Seat Entertainment", "Starlight Headliner", "Chauffeur Ready"],
        ),
        Vehicle(
            slug="ford-mustang-gt",
            make="Ford",
            model="Mustang GT",
            year=2020,
            category="muscle",
            price_per_day=299,
            status="booked",
            horsepower=460,
            zero_to_sixty=4.2,
            seats=4,
            engine="V8",
            thumbnails=[
                "https://images.unsplash.com/photo-1502877338535-766e1452684a?q=80&w=1920&auto=format&fit=crop",
            ],
            gallery=[
                "https://images.unsplash.com/photo-1502872364588-894d7d6ddfab?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=1920&auto=format&fit=crop",
            ],
            features=["Brembo Package", "Apple CarPlay", "Performance Exhaust"],
        ),
        Vehicle(
            slug="ferrari-488-gtb",
            make="Ferrari",
            model="488 GTB",
            year=2019,
            category="supercar",
            price_per_day=1399,
            status="available",
            horsepower=661,
            zero_to_sixty=3.0,
            seats=2,
            engine="V8 Twin-Turbo",
            thumbnails=[
                "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?q=80&w=1920&auto=format&fit=crop",
            ],
            gallery=[
                "https://images.unsplash.com/photo-1503736334956-4c8f8e92946d?q=80&w=1920&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=1920&auto=format&fit=crop",
            ],
            features=["Carbon Fiber Interior", "Lift System", "Race Mode"],
        ),
    ]

    sample_reviews = [
        Testimonial(name="Alex H.", rating=5, comment="Flawless delivery to my shoot in West Hollywood."),
        Testimonial(name="Dana R.", rating=4.9, comment="Concierge service was next level. Best rates in LA."),
        Testimonial(name="Studio Ops", rating=5, comment="Booked for a music video – punctual, insured, professional."),
    ]

    inserted = {"vehicles": 0, "testimonials": 0}

    for v in sample_cars:
        # Upsert-like behavior: if slug exists, skip
        existing = list(db["vehicle"].find({"slug": v.slug}).limit(1)) if db else []
        if not existing:
            create_document("vehicle", v)
            inserted["vehicles"] += 1

    for t in sample_reviews:
        # Avoid unbounded growth – only add if exact comment not present yet
        existing = list(db["testimonial"].find({"comment": t.comment}).limit(1)) if db else []
        if not existing:
            create_document("testimonial", t)
            inserted["testimonials"] += 1

    return {"inserted": inserted}


# Public API
@app.get("/vehicles", response_model=List[Vehicle])
def list_vehicles(category: Optional[str] = None):
    filt = {"category": category} if category else {}
    docs = get_documents("vehicle", filt)
    # Convert ObjectId and ensure keys exist
    clean = []
    for d in docs:
        d.pop("_id", None)
        clean.append(Vehicle(**d))
    return clean


@app.get("/vehicles/{slug}", response_model=Vehicle)
def get_vehicle(slug: str):
    docs = get_documents("vehicle", {"slug": slug})
    if not docs:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    d = docs[0]
    d.pop("_id", None)
    return Vehicle(**d)


class BookingResponse(BaseModel):
    status: str
    message: str


@app.post("/book", response_model=BookingResponse)
def book_now(payload: Booking):
    create_document("booking", payload)
    return BookingResponse(status="ok", message="Your request has been received. Our team will contact you shortly.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
