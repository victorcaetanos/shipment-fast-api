from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import DeliveryService

router = APIRouter()
delivery_service = DeliveryService()


@router.post("/deliveries/", response_model=schemas.DeliveryResponse)
def create_delivery(delivery: schemas.DeliveryCreate, db: Session = Depends(get_db)):
    return delivery_service.create_delivery(db, delivery)


@router.get("/deliveries/", response_model=list[schemas.DeliveryResponse])
def list_deliveries(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return delivery_service.get_deliveries(db, skip, limit)


@router.get("/deliveries/{delivery_id}", response_model=schemas.DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    return delivery_service.get_by_id_or_404(db, delivery_id)


@router.get("/deliveries/order/{order_id}", response_model=list[schemas.DeliveryResponse])
def get_deliveries_by_order(order_id: int, db: Session = Depends(get_db)):
    return delivery_service.get_deliveries_by_order(db, order_id)


@router.get("/deliveries/pending/", response_model=list[schemas.DeliveryResponse])
def get_pending_deliveries(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return delivery_service.get_pending_deliveries(db, skip, limit)


@router.get("/deliveries/completed/", response_model=list[schemas.DeliveryResponse])
def get_completed_deliveries(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return delivery_service.get_completed_deliveries(db, skip, limit)


@router.get("/deliveries/in-transit/", response_model=list[schemas.DeliveryResponse])
def get_deliveries_in_transit(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return delivery_service.get_deliveries_in_transit(db, skip, limit)


@router.put("/deliveries/{delivery_id}", response_model=schemas.DeliveryResponse)
def update_delivery(
        delivery_id: int,
        delivery_update: schemas.DeliveryUpdate,
        db: Session = Depends(get_db)
):
    return delivery_service.update_delivery(db, delivery_id, delivery_update)


@router.put("/deliveries/{delivery_id}/start", response_model=schemas.DeliveryResponse)
def start_delivery(delivery_id: int, db: Session = Depends(get_db)):
    return delivery_service.start_delivery(db, delivery_id)


@router.put("/deliveries/{delivery_id}/complete", response_model=schemas.DeliveryResponse)
def complete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    return delivery_service.complete_delivery(db, delivery_id)


@router.delete("/deliveries/{delivery_id}", status_code=204)
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    db_delivery = delivery_service.get_by_id_or_404(db, delivery_id)
    delivery_service.delete(db, db_obj=db_delivery)
