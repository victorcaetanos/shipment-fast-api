from typing import TypeVar, Generic, List, Optional, Dict, Any

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common CRUD operations"""

    def __init__(self, model: type[ModelType]):
        self.model = model

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        try:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity violation"
            )

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, db: Session, id: int) -> ModelType:
        """Get a record by ID or raise 404"""
        obj = self.get(db, id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found"
            )
        return obj

    def get_multi(
            self,
            db: Session,
            *,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        query = db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update a record"""
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity violation"
            )

    def delete(self, db: Session, *, db_obj: ModelType) -> None:
        """Delete a record"""
        db.delete(db_obj)
        db.commit()
