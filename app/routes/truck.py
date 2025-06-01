from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import TruckService

router = APIRouter()
truck_service = TruckService()


@router.post("/trucks/", response_model=schemas.TruckResponse)
def create_truck(truck: schemas.TruckCreate, db: Session = Depends(get_db)):
    return truck_service.create_truck(db, truck)


@router.get("/trucks/", response_model=list[schemas.TruckResponse])
def list_trucks(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return truck_service.get_trucks(db, skip, limit)


@router.get("/trucks/available/", response_model=list[schemas.TruckResponse])
def get_available_trucks(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return truck_service.get_available_trucks(db, skip, limit)


@router.get("/trucks/{truck_id}", response_model=schemas.TruckResponse)
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    return truck_service.get_by_id_or_404(db, truck_id)


@router.get("/trucks/license/{license_plate}", response_model=schemas.TruckResponse)
def get_truck_by_license_plate(license_plate: str, db: Session = Depends(get_db)):
    truck = truck_service.get_by_license_plate(db, license_plate)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.put("/trucks/{truck_id}", response_model=schemas.TruckResponse)
def update_truck(
        truck_id: int,
        truck_update: schemas.TruckUpdate,
        db: Session = Depends(get_db)
):
    return truck_service.update_truck(db, truck_id, truck_update)


@router.delete("/trucks/{truck_id}", status_code=204)
def delete_truck(truck_id: int, db: Session = Depends(get_db)):
    db_truck = truck_service.get_by_id_or_404(db, truck_id)
    truck_service.delete(db, db_obj=db_truck)
