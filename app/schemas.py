from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: str = Field(..., max_length=100)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer - inherits all fields from CustomerBase"""

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip().title()


class CustomerUpdate(BaseModel):
    """Schema for updating a customer - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)


class CustomerResponse(CustomerBase):
    """Schema for customer responses - includes the ID"""
    customer_id: int

    class Config:
        from_attributes = True


class DriverBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    cpf: str = Field(..., min_length=11, max_length=14)
    phone: Optional[str] = Field(None, max_length=20)
    license_number: str = Field(..., max_length=20)


class DriverCreate(DriverBase):
    """Schema for creating a new driver"""

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        cpf_clean = v.replace('.', '').replace('-', '').replace(' ', '')
        if len(cpf_clean) != 11 or not cpf_clean.isdigit():
            raise ValueError('CPF must have exactly 11 digits')
        return cpf_clean

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip().title()


class DriverUpdate(BaseModel):
    """Schema for updating a driver"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    cpf: Optional[str] = Field(None, min_length=11, max_length=14)
    phone: Optional[str] = Field(None, max_length=20)
    license_number: Optional[str] = Field(None, max_length=20)


class DriverResponse(DriverBase):
    """Schema for driver responses"""
    driver_id: int

    class Config:
        from_attributes = True


class TruckBase(BaseModel):
    license_plate: str = Field(..., min_length=7, max_length=10)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    capacity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class TruckCreate(TruckBase):
    """Schema for creating a new truck"""

    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: str) -> str:
        return v.upper().replace(' ', '').replace('-', '')


class TruckUpdate(BaseModel):
    """Schema for updating a truck"""
    license_plate: Optional[str] = Field(None, min_length=7, max_length=10)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    capacity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class TruckResponse(TruckBase):
    """Schema for truck responses"""
    truck_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: int = Field(..., gt=0)
    driver_id: int = Field(..., gt=0)
    truck_id: int = Field(..., gt=0)
    order_date: date
    status: str = Field(..., max_length=20)


class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    status: str = Field(default="pending", max_length=20)

    @field_validator('order_date')
    @classmethod
    def validate_order_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Order date cannot be in the past')
        return v


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    customer_id: Optional[int] = Field(None, gt=0)
    driver_id: Optional[int] = Field(None, gt=0)
    truck_id: Optional[int] = Field(None, gt=0)
    order_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)


class OrderResponse(OrderBase):
    """Schema for order responses"""
    order_id: int

    class Config:
        from_attributes = True


class DeliveryBase(BaseModel):
    order_id: int = Field(..., gt=0)
    departure_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    origin: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    """Schema for creating a new delivery"""

    @field_validator('delivery_time')
    @classmethod
    def validate_delivery_time(cls, v: Optional[datetime], info) -> Optional[datetime]:

        if v and hasattr(info, 'data') and info.data.get('departure_time'):
            departure_time = info.data['departure_time']
            if v <= departure_time:
                raise ValueError('Delivery time must be after departure time')
        return v


class DeliveryUpdate(BaseModel):
    """Schema for updating a delivery"""
    order_id: Optional[int] = Field(None, gt=0)
    departure_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    origin: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class DeliveryResponse(DeliveryBase):
    """Schema for delivery responses"""
    delivery_id: int

    class Config:
        from_attributes = True
