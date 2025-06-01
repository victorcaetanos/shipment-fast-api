from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Delivery
from .base_service import BaseService
from .order_service import OrderService


class DeliveryService(BaseService[Delivery, schemas.DeliveryCreate, schemas.DeliveryUpdate]):
    """Service for Delivery operations"""

    def __init__(self):
        super().__init__(Delivery)
        self.order_service = OrderService()

    def get_by_id(self, db: Session, delivery_id: int) -> Optional[Delivery]:
        """Get delivery by ID"""
        return db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()

    def get_by_id_or_404(self, db: Session, delivery_id: int) -> Delivery:
        """Get delivery by ID or raise 404"""
        delivery = self.get_by_id(db, delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found"
            )
        return delivery

    def get_deliveries(self, db: Session, skip: int = 0, limit: int = 10) -> List[Delivery]:
        """Get list of deliveries with pagination"""
        return db.query(Delivery).offset(skip).limit(limit).all()

    def create_delivery(self, db: Session, delivery_data: schemas.DeliveryCreate) -> Delivery:
        """Create a new delivery with order validation"""
        self.order_service.get_by_id_or_404(db, delivery_data.order_id)

        return self.create(db, obj_in=delivery_data)

    def update_delivery(
            self,
            db: Session,
            delivery_id: int,
            delivery_update: schemas.DeliveryUpdate
    ) -> Delivery:
        """Update delivery with order validation"""
        db_delivery = self.get_by_id_or_404(db, delivery_id)

        if delivery_update.order_id:
            self.order_service.get_by_id_or_404(db, delivery_update.order_id)

        return self.update(db, db_obj=db_delivery, obj_in=delivery_update)

    def get_deliveries_by_order(self, db: Session, order_id: int) -> List[Delivery]:
        """Get deliveries for a specific order"""
        self.order_service.get_by_id_or_404(db, order_id)

        return db.query(Delivery).filter(Delivery.order_id == order_id).all()

    def get_pending_deliveries(self, db: Session, skip: int = 0, limit: int = 10) -> List[Delivery]:
        """Get pending deliveries (no delivery time set)"""
        return db.query(Delivery).filter(
            Delivery.delivery_time.is_(None)
        ).offset(skip).limit(limit).all()

    def get_completed_deliveries(self, db: Session, skip: int = 0, limit: int = 10) -> List[Delivery]:
        """Get completed deliveries (delivery time is set)"""
        return db.query(Delivery).filter(
            Delivery.delivery_time.isnot(None)
        ).offset(skip).limit(limit).all()

    def get_deliveries_in_transit(self, db: Session, skip: int = 0, limit: int = 10) -> List[Delivery]:
        """Get deliveries in transit (departed but not delivered)"""
        return db.query(Delivery).filter(
            Delivery.departure_time.isnot(None),
            Delivery.delivery_time.is_(None)
        ).offset(skip).limit(limit).all()

    def start_delivery(self, db: Session, delivery_id: int) -> Delivery:
        """Mark delivery as started (set departure time)"""
        db_delivery = self.get_by_id_or_404(db, delivery_id)

        if db_delivery.departure_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery has already started"
            )

        db_delivery.departure_time = datetime.now()
        db.commit()
        db.refresh(db_delivery)
        return db_delivery

    def complete_delivery(self, db: Session, delivery_id: int) -> Delivery:
        """Mark delivery as completed (set delivery time)"""
        db_delivery = self.get_by_id_or_404(db, delivery_id)

        if db_delivery.delivery_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery has already been completed"
            )

        if not db_delivery.departure_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivery must be started before it can be completed"
            )

        db_delivery.delivery_time = datetime.now()
        db.commit()
        db.refresh(db_delivery)
        return db_delivery
