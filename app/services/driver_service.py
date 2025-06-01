from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Driver
from .base_service import BaseService


class DriverService(BaseService[Driver, schemas.DriverCreate, schemas.DriverUpdate]):
    """Service for Driver operations"""

    def __init__(self):
        super().__init__(Driver)

    def get_by_id(self, db: Session, driver_id: int) -> Optional[Driver]:
        """Get driver by ID"""
        return db.query(Driver).filter(Driver.driver_id == driver_id).first()

    def get_by_id_or_404(self, db: Session, driver_id: int) -> Driver:
        """Get driver by ID or raise 404"""
        driver = self.get_by_id(db, driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        return driver

    def get_drivers(self, db: Session, skip: int = 0, limit: int = 10) -> List[Driver]:
        """Get list of drivers with pagination"""
        return db.query(Driver).offset(skip).limit(limit).all()

    def get_by_cpf(self, db: Session, cpf: str) -> Optional[Driver]:
        """Get driver by CPF"""
        return db.query(Driver).filter(Driver.cpf == cpf).first()

    def create_driver(self, db: Session, driver_data: schemas.DriverCreate) -> Driver:
        """Create a new driver with CPF validation"""
        existing_driver = self.get_by_cpf(db, driver_data.cpf)
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver with this CPF already exists"
            )

        return self.create(db, obj_in=driver_data)

    def update_driver(
            self,
            db: Session,
            driver_id: int,
            driver_update: schemas.DriverUpdate
    ) -> Driver:
        """Update driver with CPF validation"""
        db_driver = self.get_by_id_or_404(db, driver_id)

        if driver_update.cpf:
            existing_driver = self.get_by_cpf(db, driver_update.cpf)
            if existing_driver and existing_driver.driver_id != driver_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Driver with this CPF already exists"
                )

        return self.update(db, db_obj=db_driver, obj_in=driver_update)
