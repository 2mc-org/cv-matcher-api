import logging
from typing import Any

from sqlmodel import SQLModel

from app.core.base_repository import BaseRepository

type ServicePatchPayload = SQLModel | dict[str, Any]


class BaseService[
    T: SQLModel,
    TPatch: ServicePatchPayload = ServicePatchPayload,
]:
    def __init__(self, repo: BaseRepository[T, TPatch]) -> None:
        self.repo = repo
        self.model = repo.model

        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
