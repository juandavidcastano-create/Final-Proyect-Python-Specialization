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
        return self.save(instance)

    def add(self, instance: ModelType) -> None:
        """Add an instance to the session (no commit)."""
        self.db.add(instance)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def refresh(self, instance: ModelType) -> None:
        """Refresh an instance from the database."""
        self.db.refresh(instance)

    def save(self, instance: ModelType) -> ModelType:
        """Add, commit and refresh an instance, returning it."""
        self.add(instance)
        self.commit()
        self.refresh(instance)
        return instance

    def delete_by_id(self, object_id: int):
        instance = self.get_by_id(object_id)
        if not instance:
            return None
        self.delete(instance)
        self.commit()
        return instance

    def delete(self, instance: ModelType) -> None:
        """Delete an instance from the session."""
        self.db.delete(instance)
        self.commit()
