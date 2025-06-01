from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Order
from .base_service import BaseService
from .customer_service import CustomerService
from .driver_service import DriverService
from .truck_service import TruckService


class OrderService(BaseService[Order, schemas.OrderCreate, schemas.OrderUpdate]):
    """Service for Order operations"""

    def __init__(self):
        super().__init__(Order)
        self.customer_service = CustomerService()
        self.driver_service = DriverService()
        self.truck_service = TruckService()

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.order_id == order_id).first()

    def get_by_id_or_404(self, db: Session, order_id: int) -> Order:
        """Get order by ID or raise 404"""
        order = self.get_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order

    def get_orders(self, db: Session, skip: int = 0, limit: int = 10) -> List[Order]:
        """Get list of orders with pagination"""
        return db.query(Order).offset(skip).limit(limit).all()

    def create_order(self, db: Session, order_data: schemas.OrderCreate) -> Order:
        """Create a new order with validation"""
        self.customer_service.get_by_id_or_404(db, order_data.customer_id)
        self.driver_service.get_by_id_or_404(db, order_data.driver_id)
        self.truck_service.get_by_id_or_404(db, order_data.truck_id)

        return self.create(db, obj_in=order_data)

    def update_order(
            self,
            db: Session,
            order_id: int,
            order_update: schemas.OrderUpdate
    ) -> Order:
        """Update order with validation"""
        db_order = self.get_by_id_or_404(db, order_id)

        if order_update.customer_id:
            self.customer_service.get_by_id_or_404(db, order_update.customer_id)

        if order_update.driver_id:
            self.driver_service.get_by_id_or_404(db, order_update.driver_id)

        if order_update.truck_id:
            self.truck_service.get_by_id_or_404(db, order_update.truck_id)

        return self.update(db, db_obj=db_order, obj_in=order_update)

    def get_orders_by_customer(
            self,
            db: Session,
            customer_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Order]:
        """Get orders for a specific customer"""
        self.customer_service.get_by_id_or_404(db, customer_id)

        return db.query(Order).filter(
            Order.customer_id == customer_id
        ).offset(skip).limit(limit).all()

    def get_orders_by_driver(
            self,
            db: Session,
            driver_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Order]:
        """Get orders for a specific driver"""
        self.driver_service.get_by_id_or_404(db, driver_id)

        return db.query(Order).filter(
            Order.driver_id == driver_id
        ).offset(skip).limit(limit).all()

    def get_orders_by_status(
            self,
            db: Session,
            status: str,
            skip: int = 0,
            limit: int = 10
    ) -> List[Order]:
        """Get orders by status"""
        return db.query(Order).filter(
            Order.status == status
        ).offset(skip).limit(limit).all()

    def get_active_orders(self, db: Session, skip: int = 0, limit: int = 10) -> List[Order]:
        """Get active orders (pending or in progress)"""
        return db.query(Order).filter(
            Order.status.in_(["pending", "in_progress"])
        ).offset(skip).limit(limit).all()

    def complete_order(self, db: Session, order_id: int) -> Order:
        """Mark an order as completed"""
        db_order = self.get_by_id_or_404(db, order_id)
        db_order.status = "completed"
        db.commit()
        db.refresh(db_order)
        return db_order
