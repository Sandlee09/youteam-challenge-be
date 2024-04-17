from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Define SQLAlchemy model for column_relationships table
class ColumnRelationship(Base):
    __tablename__ = "column_relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    target = Column(String, nullable=False)
    type = Column(String, nullable=False)



class Customer(Base):
    __tablename__ = "customers"

    CustomerID = Column(Integer, primary_key=True)
    FirstName = Column(String(255))
    LastName = Column(String(255))
    Email = Column(String(255))
    PasswordHash = Column(String(255))
    Address = Column(String(255))
    City = Column(String(255))
    State = Column(String(255))
    ZipCode = Column(String(10))
    Country = Column(String(255))
    Phone = Column(String(20))

    orders = relationship("Order", backref="customer")
    reviews = relationship("Review", backref="customer")

class Product(Base):
    __tablename__ = "products"

    ProductID = Column(Integer, primary_key=True)
    Name = Column(String(255))
    Description = Column(String)
    Price = Column(Numeric)
    StockQuantity = Column(Integer)
    CategoryID = Column(Integer, ForeignKey("categories.CategoryID"))

    category = relationship("Category", backref="products")
    order_details = relationship("OrderDetail", backref="product")
    reviews = relationship("Review", backref="product")
    inventory = relationship("Inventory", backref="product")

class Category(Base):
    __tablename__ = "categories"

    CategoryID = Column(Integer, primary_key=True)
    Name = Column(String(255))
    Description = Column(String)

class Order(Base):
    __tablename__ = "orders"

    OrderID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"))
    OrderDate = Column(DateTime)
    ShippingAddress = Column(String(255))
    TotalAmount = Column(Numeric)

    order_details = relationship("OrderDetail", backref="order")
    shipping = relationship("Shipping", backref="order")
    payments = relationship("Payment", backref="order")

class OrderDetail(Base):
    __tablename__ = "order_details"

    OrderDetailID = Column(Integer, primary_key=True)
    OrderID = Column(Integer, ForeignKey("orders.OrderID"))
    ProductID = Column(Integer, ForeignKey("products.ProductID"))
    Amount = Column(Numeric)
    Quantity = Column(Integer)
    UnitPrice = Column(Numeric)

class Supplier(Base):
    __tablename__ = "suppliers"

    SupplierID = Column(Integer, primary_key=True)
    Name = Column(String(255))
    ContactName = Column(String(255))
    Address = Column(String(255))
    City = Column(String(255))
    State = Column(String(255))
    Country = Column(String(255))
    Phone = Column(String(20))

class Inventory(Base):
    __tablename__ = "inventory"

    InventoryID = Column(Integer, primary_key=True)
    ProductID = Column(Integer, ForeignKey("products.ProductID"))
    QuantityAvailable = Column(Integer)
    WarehouseLocation = Column(String(255))

class Shipping(Base):
    __tablename__ = "shipping"

    ShippingID = Column(Integer, primary_key=True)
    OrderID = Column(Integer, ForeignKey("orders.OrderID"))
    ShippingDate = Column(DateTime)
    Carrier = Column(String(255))
    TrackingNumber = Column(String(255))

class Payment(Base):
    __tablename__ = "payments"

    PaymentID = Column(Integer, primary_key=True)
    OrderID = Column(Integer, ForeignKey("orders.OrderID"))
    PaymentDate = Column(DateTime)
    Amount = Column(Numeric)
    PaymentMethod = Column(String(255))

class Review(Base):
    __tablename__ = "reviews"

    ReviewID = Column(Integer, primary_key=True)
    ProductID = Column(Integer, ForeignKey("products.ProductID"))
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"))
    Rating = Column(Integer)
    Comment = Column(String)
    ReviewDate = Column(DateTime)