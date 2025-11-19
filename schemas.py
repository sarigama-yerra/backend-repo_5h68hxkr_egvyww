"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Users are optional for this app, keeping example for reference
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    character: str = Field(..., description="Anime character inspiration (e.g., Naruto, Levi)")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    colors: List[str] = Field(default_factory=list, description="Available colors")
    sizes: List[str] = Field(default_factory=lambda: ["S","M","L","XL"], description="Available sizes")
    image: Optional[str] = Field(None, description="Primary image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product ObjectId as string")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    size: Optional[str] = Field(None, description="Selected size")
    color: Optional[str] = Field(None, description="Selected color")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem]
    customer_name: str
    customer_email: EmailStr
    customer_address: str
    note: Optional[str] = None
    status: str = Field("pending", description="Order status")
