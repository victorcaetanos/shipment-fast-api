from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Truck
from .base_service import BaseService


class TruckService(BaseService[Truck, schemas.TruckCreate, schemas.TruckUpdate]):
    """Service for Truck operations"""

    def __init__(self):
        super().__init__(Truck)

    def get_by_id(self, db: Session, truck_id: int) -> Optional[Truck]:
        """Get truck by ID"""
        return db.query(Truck).filter(Truck.truck_id == truck_id).first()

    def get_by_id_or_404(self, db: Session, truck_id: int) -> Truck:
        """Get truck by ID or raise 404"""
        truck = self.get_by_id(db, truck_id)
        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Truck not found"
            )
        return truck

    def get_trucks(self, db: Session, skip: int = 0, limit: int = 10) -> List[Truck]:
        """Get list of trucks with pagination"""
        return db.query(Truck).offset(skip).limit(limit).all()

    def get_by_license_plate(self, db: Session, license_plate: str) -> Optional[Truck]:
        """Get truck by license plate"""
        return db.query(Truck).filter(Truck.license_plate == license_plate).first()

    def create_truck(self, db: Session, truck_data: schemas.TruckCreate) -> Truck:
        """Create a new truck with license plate validation"""
        existing_truck = self.get_by_license_plate(db, truck_data.license_plate)
        if existing_truck:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Truck with this license plate already exists"
            )

        return self.create(db, obj_in=truck_data)

    def update_truck(
            self,
            db: Session,
            truck_id: int,
            truck_update: schemas.TruckUpdate
    ) -> Truck:
        """Update truck with license plate validation"""
        db_truck = self.get_by_id_or_404(db, truck_id)

        if truck_update.license_plate:
            existing_truck = self.get_by_license_plate(db, truck_update.license_plate)
            if existing_truck and existing_truck.truck_id != truck_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Truck with this license plate already exists"
                )

        return self.update(db, db_obj=db_truck, obj_in=truck_update)

    def get_available_trucks(self, db: Session, skip: int = 0, limit: int = 10) -> List[Truck]:
        """Get trucks that are not currently assigned to active orders"""
        from app.models import Order

        active_truck_ids = db.query(Order.truck_id).filter(
            Order.status.in_(["pending", "in_progress"])
        ).subquery()

        return db.query(Truck).filter(
            ~Truck.truck_id.in_(active_truck_ids)
        ).offset(skip).limit(limit).all()
