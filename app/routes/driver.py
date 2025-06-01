from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import DriverService

router = APIRouter()
driver_service = DriverService()


@router.post("/drivers/", response_model=schemas.DriverResponse)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    return driver_service.create_driver(db, driver)


@router.get("/drivers/", response_model=list[schemas.DriverResponse])
def list_drivers(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    return driver_service.get_drivers(db, skip, limit)


@router.get("/drivers/{driver_id}", response_model=schemas.DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    return driver_service.get_by_id_or_404(db, driver_id)


@router.get("/drivers/cpf/{cpf}", response_model=schemas.DriverResponse)
def get_driver_by_cpf(cpf: str, db: Session = Depends(get_db)):
    driver = driver_service.get_by_cpf(db, cpf)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.put("/drivers/{driver_id}", response_model=schemas.DriverResponse)
def update_driver(
        driver_id: int,
        driver_update: schemas.DriverUpdate,
        db: Session = Depends(get_db)
):
    return driver_service.update_driver(db, driver_id, driver_update)


@router.delete("/drivers/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    db_driver = driver_service.get_by_id_or_404(db, driver_id)
    driver_service.delete(db, db_obj=db_driver)
