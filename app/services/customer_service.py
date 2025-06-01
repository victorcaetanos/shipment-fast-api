from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Customer
from .base_service import BaseService


class CustomerService(BaseService[Customer, schemas.CustomerCreate, schemas.CustomerUpdate]):
    """Service for Customer operations"""

    def __init__(self):
        super().__init__(Customer)

    def get_by_id(self, db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(Customer.customer_id == customer_id).first()

    def get_by_id_or_404(self, db: Session, customer_id: int) -> Customer:
        """Get customer by ID or raise 404"""
        customer = self.get_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer

    def get_customers(self, db: Session, skip: int = 0, limit: int = 10) -> List[Customer]:
        """Get list of customers with pagination"""
        return db.query(Customer).offset(skip).limit(limit).all()

    def get_by_email(self, db: Session, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return db.query(Customer).filter(Customer.email == email).first()

    def search_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 10) -> List[Customer]:
        """Search customers by name"""
        return db.query(Customer).filter(
            Customer.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()
