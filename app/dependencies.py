from functools import lru_cache

from app.services import (
    CustomerService,
    DriverService,
    TruckService,
    OrderService,
    DeliveryService
)


@lru_cache()
def get_customer_service() -> CustomerService:
    """Dependency to get CustomerService instance"""
    return CustomerService()


@lru_cache()
def get_driver_service() -> DriverService:
    """Dependency to get DriverService instance"""
    return DriverService()


@lru_cache()
def get_truck_service() -> TruckService:
    """Dependency to get TruckService instance"""
    return TruckService()


@lru_cache()
def get_order_service() -> OrderService:
    """Dependency to get OrderService instance"""
    return OrderService()


@lru_cache()
def get_delivery_service() -> DeliveryService:
    """Dependency to get DeliveryService instance"""
    return DeliveryService()
