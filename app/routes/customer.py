from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import CustomerService

router = APIRouter()
customer_service = CustomerService()


@router.post("/customers/", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create(db, obj_in=customer)


@router.get("/customers/", response_model=list[schemas.CustomerResponse])
def list_customers(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return customer_service.get_customers(db, skip, limit)


@router.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return customer_service.get_by_id_or_404(db, customer_id)


@router.get("/customers/search/", response_model=list[schemas.CustomerResponse])
def search_customers_by_name(
        name: str = Query(..., min_length=1),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return customer_service.search_by_name(db, name, skip, limit)


@router.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
        customer_id: int,
        customer_update: schemas.CustomerUpdate,
        db: Session = Depends(get_db)
):
    db_customer = customer_service.get_by_id_or_404(db, customer_id)
    return customer_service.update(db, db_obj=db_customer, obj_in=customer_update)


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = customer_service.get_by_id_or_404(db, customer_id)
    customer_service.delete(db, db_obj=db_customer)
