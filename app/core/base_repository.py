from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlmodel import SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

from app.core.db.database import session_ctx

type PatchPayload = SQLModel | dict[str, Any]


class BaseRepository[T: SQLModel, TPatch: PatchPayload = PatchPayload]:
    """
    Generic base repository with common CRUD operations.
    """

    def __init__(
        self,
        model: type[T],
        *,
        expand_mapping: dict[Any, list[InstrumentedAttribute[Any]]]
        | None = None,
    ):
        """
        Initialize repository with model class and database session.

        Args:
            model_class: SQLModel class to operate on
            session: Database session
        """
        self.model = model
        self.session = session_ctx.get()
        self.expand_mapping = expand_mapping or {}

    def _pk_id_column(self) -> Any:
        """Return the mapped `id` column; models used with get_by_id must define it."""
        if not hasattr(self.model, "id"):
            raise TypeError(
                f"{self.model.__name__} must define an 'id' field for "
                f"{type(self).__name__}.get_by_id / delete",
            )
        return cast(Any, self.model).id

    def build_selectinloads(
        self,
        expand: list[Any],
        mapping: dict[str, list[InstrumentedAttribute[Any]]],
    ) -> list[list[InstrumentedAttribute[Any]]]:
        selectinloads = []
        for key, path in mapping.items():
            if key in expand:
                selectinloads.append(path)
        return selectinloads

    def stmt(
        self,
        *,
        selectinloads: list[list[InstrumentedAttribute[Any]]] | None = None,
        expands: list[Any] | None = None,
    ) -> SelectOfScalar[T]:
        """
        Create base select statement with optional selectinloads.

        Args:
            selectinloads: List of relationship chains to eager load

        Returns:
            Select statement for the model
        """
        stmt = select(self.model)
        if expands:
            selectinloads = (selectinloads or []) + self.build_selectinloads(
                expands, self.expand_mapping
            )

        if selectinloads:
            options = []
            for chain in selectinloads:
                if not chain:
                    continue
                loader = selectinload(chain[0])
                for rel in chain[1:]:
                    loader = loader.selectinload(rel)
                options.append(loader)
            stmt = stmt.options(*options)
        return stmt

    async def fetch_count(self, stmt: SelectOfScalar[T]) -> int:
        """
        Fetch count of entities from select statement.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            Count of entities
        """
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar()
        return total or 0

    async def exists(self, stmt: SelectOfScalar[T]) -> bool:
        """
        Check if any entities exist in the select statement.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            True if entities exist, False otherwise
        """

        total = await self.fetch_count(stmt)
        return total > 0

    async def fetch_one_or_rise(self, stmt: SelectOfScalar[T]) -> T:
        """
        Fetch one entity or raise HTTP 404 if not found.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            Found entity

        Raises:
            HTTPException: If entity not found
        """
        result = await self.session.execute(stmt)
        data = result.scalars().first()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return data

    async def fetch_one(self, stmt: SelectOfScalar[T]) -> T | None:
        """
        Fetch one entity or return None if not found.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            Found entity or None
        """
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def fetch_many(self, stmt: SelectOfScalar[T]) -> Sequence[T]:
        """
        Fetch multiple entities.

        Args:
            stmt: SQLAlchemy select statement

        Returns:
            Sequence of found entities
        """
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, id: UUID | None, *, expand: list[Any] | None = None
    ) -> T | None:
        """
        Get entity by id.

        Args:
            id: UUID of the entity

        Returns:
            Entity or None if not found or id is None
        """
        if id is None:
            return None

        # return await self.session.get(self.model_class, id)
        stmt = self.stmt(expands=expand)
        stmt = stmt.where(self._pk_id_column() == id)
        return await self.fetch_one(stmt)

    async def get_by_id_or_raise(
        self, id: UUID | None, *, expand: list[Any] | None = None
    ) -> T:
        """
        Get entity by id or raise HTTPException if not found.

        Args:
            id: UUID of the entity

        Returns:
            Found entity

        Raises:
            HTTPException: If entity not found
        """

        if id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )

        entity = await self.get_by_id(id, expand=expand)
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} not found",
            )
        return entity

    async def add(
        self,
        entity: T,
        *,
        commit: bool = True,
    ) -> T:
        """
        Add new entity.

        Args:
            entity: Entity to add

        Returns:
            Added entity with generated id
        """
        self.session.add(entity)
        if commit:
            await self.session.commit()
            await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """
        Update existing entity.

        Args:
            entity: Entity with updated fields

        Returns:
            Updated entity
        """
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def patch(self, entity: T, data: TPatch) -> T:
        """
        Apply partial update to an already-loaded entity.
        """
        payload: dict[str, Any]
        if isinstance(data, SQLModel):
            payload = data.model_dump(exclude_unset=True)
        else:
            payload = data
        entity.sqlmodel_update(payload)
        return await self.update(entity)

    async def patch_by_id(self, id: UUID, data: TPatch) -> T:
        """
        Load entity by id and apply partial update.
        """
        entity = await self.get_by_id_or_raise(id)
        return await self.patch(entity, data)

    async def delete(self, id: UUID) -> None:
        """
        Delete entity by id.

        Args:
            id: UUID of entity to delete

        Raises:
            HTTPException: If entity doesn't exist
        """
        entity = await self.get_by_id_or_raise(id)

        await self.session.delete(entity)
        await self.session.commit()
