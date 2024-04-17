from pydantic import BaseModel
from typing import List, Optional

# Define your Pydantic models for the tables
class Customer(BaseModel):
    CustomerID: int
    FirstName: str
    LastName: str
    Email: str
    PasswordHash: str
    Address: str
    City: str
    State: str
    ZipCode: str
    Country: str
    Phone: str

class Product(BaseModel):
    ProductID: int
    Name: str
    Description: str
    Price: float
    StockQuantity: int
    CategoryID: int

class Category(BaseModel):
    CategoryID: int
    Name: str
    Description: str

class Order(BaseModel):
    OrderID: int
    CustomerID: int
    OrderDate: str
    ShippingAddress: str
    TotalAmount: float

class OrderDetail(BaseModel):
    OrderDetailID: int
    OrderID: int
    ProductID: int
    Amount: float
    Quantity: int
    UnitPrice: float

class Supplier(BaseModel):
    SupplierID: int
    Name: str
    ContactName: str
    Address: str
    City: str
    State: str
    Country: str
    Phone: str

class Inventory(BaseModel):
    InventoryID: int
    ProductID: int
    QuantityAvailable: int
    WarehouseLocation: str

class Shipping(BaseModel):
    ShippingID: int
    OrderID: int
    ShippingDate: str
    Carrier: str
    TrackingNumber: str

class Payment(BaseModel):
    PaymentID: int
    OrderID: int
    PaymentDate: str
    Amount: float
    PaymentMethod: str

class Review(BaseModel):
    ReviewID: int
    ProductID: int
    CustomerID: int
    Rating: int
    Comment: str
    ReviewDate: str