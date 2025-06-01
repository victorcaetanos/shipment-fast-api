from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100))


class Driver(Base):
    __tablename__ = "drivers"
    driver_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    phone = Column(String(20))
    license_number = Column(String(20), nullable=False)


class Truck(Base):
    __tablename__ = "trucks"
    truck_id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(10), unique=True, nullable=False)
    model = Column(String(50))
    year = Column(Integer)
    capacity = Column(Numeric(10, 2))


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    truck_id = Column(Integer, ForeignKey("trucks.truck_id"), nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)

    customer = relationship("Customer")
    driver = relationship("Driver")
    truck = relationship("Truck")


class Delivery(Base):
    __tablename__ = "deliveries"
    delivery_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    departure_time = Column(TIMESTAMP)
    delivery_time = Column(TIMESTAMP)
    origin = Column(String(200))
    destination = Column(String(200))
    notes = Column(Text)

    order = relationship("Order")
