from typing import Generic, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, object_id: int):
        return self.db.query(self.model).filter(self.model.id == object_id).first()

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete_by_id(self, object_id: int):
        instance = self.get_by_id(object_id)
        if not instance:
            return None
        self.db.delete(instance)
        self.db.commit()
        return instance
