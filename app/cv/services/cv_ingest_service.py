"""Ingest CV snapshot entries into Qdrant."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import TypeAdapter

from app.cv.schemas.cv_chunk import (
    CvCertificateChunkPayload,
    CvChunkPayload,
    CvEmploymentChunkPayload,
    CvProfileChunkPayload,
    CvSkillsChunkPayload,
)
from app.cv.schemas.cv_snapshot import CvSnapshotEntry
from app.cv.services.cv_embedding_service import CvEmbeddingService
from app.cv.services.cv_qdrant_repository import CvQdrantRepository

SNAPSHOT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "roster_profile_snapshot_2026-06-10.json"
)


class CvIngestService:
    """Build chunk payloads, embed text, and upsert points into Qdrant."""

    def __init__(
        self,
        embedding_service: CvEmbeddingService,
        qdrant_repository: CvQdrantRepository,
    ) -> None:
        self._embedding = embedding_service
        self._qdrant = qdrant_repository
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @staticmethod
    def build_chunks(entry: CvSnapshotEntry) -> list[CvChunkPayload]:
        profile = entry.profile
        return [
            CvProfileChunkPayload.from_snapshot(entry),
            CvSkillsChunkPayload.from_snapshot(entry),
            *[
                CvEmploymentChunkPayload.from_snapshot(profile, employment)
                for employment in entry.employment_history
            ],
            *[
                CvCertificateChunkPayload.from_snapshot(profile, certificate)
                for certificate in entry.certificates
            ],
        ]

    def ingest_entry(self, entry: CvSnapshotEntry) -> int:
        chunks = self.build_chunks(entry)
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        dense_vectors = self._embedding.embed_dense_texts(texts)
        sparse_vectors = self._embedding.embed_sparse_texts(texts)
        self._qdrant.ensure_collection()
        self._qdrant.upsert_chunks(chunks, dense_vectors, sparse_vectors)

        self.logger.info(
            "Ingested %s chunks for profile %s",
            len(chunks),
            entry.profile.id,
        )
        return len(chunks)

    def ingest_entries(self, entries: list[CvSnapshotEntry]) -> int:
        return sum(self.ingest_entry(entry) for entry in entries)

    def reindex_all(self) -> int:
        self._qdrant.reset_collection()
        entries = self.get_all_entries()
        return self.ingest_entries(entries)

    def get_all_entries(self) -> list[CvSnapshotEntry]:
        return TypeAdapter(list[CvSnapshotEntry]).validate_python(
            json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")),
        )
