from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import OrderService

router = APIRouter()
order_service = OrderService()


@router.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db, order)


@router.get("/orders/", response_model=list[schemas.OrderResponse])
def list_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return order_service.get_orders(db, skip, limit)


@router.get("/orders/active/", response_model=list[schemas.OrderResponse])
def get_active_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return order_service.get_active_orders(db, skip, limit)


@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_by_id_or_404(db, order_id)


@router.get("/orders/customer/{customer_id}", response_model=list[schemas.OrderResponse])
def get_orders_by_customer(
        customer_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return order_service.get_orders_by_customer(db, customer_id, skip, limit)


@router.get("/orders/driver/{driver_id}", response_model=list[schemas.OrderResponse])
def get_orders_by_driver(
        driver_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return order_service.get_orders_by_driver(db, driver_id, skip, limit)


@router.get("/orders/status/{status}", response_model=list[schemas.OrderResponse])
def get_orders_by_status(
        status: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return order_service.get_orders_by_status(db, status, skip, limit)


@router.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def update_order(
        order_id: int,
        order_update: schemas.OrderUpdate,
        db: Session = Depends(get_db)
):
    return order_service.update_order(db, order_id, order_update)


@router.put("/orders/{order_id}/complete", response_model=schemas.OrderResponse)
def complete_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.complete_order(db, order_id)


@router.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = order_service.get_by_id_or_404(db, order_id)
    order_service.delete(db, db_obj=db_order)
