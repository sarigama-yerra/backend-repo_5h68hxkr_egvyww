import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Anime Outfit Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities to handle ObjectId conversion

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

# Seed some initial products if collection empty
async def seed_products():
    if db is None:
        return
    count = db["product"].count_documents({})
    if count == 0:
        seed_data = [
            {
                "title": "Shadow Ninja Hoodie",
                "character": "Itachi",
                "description": "Oversized streetwear hoodie inspired by Itachi's cloak.",
                "price": 59.99,
                "colors": ["black", "white", "purple"],
                "sizes": ["S","M","L","XL"],
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
            },
            {
                "title": "Thunder Breather Jacket",
                "character": "Zenitsu",
                "description": "Lightweight coach jacket with subtle lightning pattern.",
                "price": 74.99,
                "colors": ["black", "white", "purple"],
                "sizes": ["S","M","L","XL"],
                "image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
            },
            {
                "title": "Survey Corps Cloak",
                "character": "Levi",
                "description": "Minimalist green cloak reimagined in monochrome.",
                "price": 89.99,
                "colors": ["black", "white", "purple"],
                "sizes": ["S","M","L","XL"],
                "image": "https://images.unsplash.com/photo-1520975922284-5f5730b979bc?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
            },
        ]
        db["product"].insert_many(seed_data)

@app.on_event("startup")
async def startup_event():
    try:
        await seed_products()
    except Exception:
        pass

@app.get("/")
def read_root():
    return {"message": "Anime Outfit Shop API running"}

@app.get("/api/products")
def list_products(character: Optional[str] = None, color: Optional[str] = None, q: Optional[str] = None):
    if db is None:
        # Return static fallback so frontend can render without DB
        fallback = [
            {"id": "1", "title": "Shadow Ninja Hoodie", "character": "Itachi", "price": 59.99, "colors": ["black","white","purple"], "image": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200&auto=format&fit=crop"},
            {"id": "2", "title": "Thunder Breather Jacket", "character": "Zenitsu", "price": 74.99, "colors": ["black","white","purple"], "image": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1200&auto=format&fit=crop"},
            {"id": "3", "title": "Survey Corps Cloak", "character": "Levi", "price": 89.99, "colors": ["black","white","purple"], "image": "https://images.unsplash.com/photo-1520975922284-5f5730b979bc?q=80&w=1200&auto=format&fit=crop"},
        ]
        return fallback

    filt = {}
    if character:
        filt["character"] = {"$regex": character, "$options": "i"}
    if color:
        filt["colors"] = color
    if q:
        filt["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"character": {"$regex": q, "$options": "i"}},
        ]

    products = list(db["product"].find(filt))
    return [to_str_id(p) for p in products]

class CreateOrder(BaseModel):
    items: List[dict]
    customer_name: str
    customer_email: str
    customer_address: str
    note: Optional[str] = None

@app.post("/api/orders")
def create_order(payload: CreateOrder):
    try:
        order_id = create_document("order", payload.model_dump())
        return {"id": order_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
