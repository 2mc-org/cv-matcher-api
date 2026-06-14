"""Qdrant persistence for CV chunk points."""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Condition,
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    Prefetch,
    Rrf,
    RrfQuery,
    ScoredPoint,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.core.environments import environments
from app.cv.enums.chunk_type import CvChunkType
from app.cv.models.cv_chunk import CvChunkPayload
from app.cv.services.cv_embedding_service import CvEmbeddingService

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


class CvQdrantRepository:
    """Upsert CV chunks into a single hybrid Qdrant collection."""

    def __init__(self, embedding_service: CvEmbeddingService) -> None:
        self._embedding = embedding_service
        self._client = QdrantClient(url=environments.QDRANT_URL)
        self._collection_name = environments.QDRANT_CV_COLLECTION

    def _create_collection(self) -> None:
        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config={
                DENSE_VECTOR_NAME: VectorParams(
                    size=self._embedding.dense_vector_size,
                    distance=Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: SparseVectorParams(),
            },
        )
        self._create_payload_indexes()

    def _create_payload_indexes(self) -> None:
        for field_name in ("chunk_type", "profile_id"):
            self._client.create_payload_index(
                collection_name=self._collection_name,
                field_name=field_name,
                field_schema=PayloadSchemaType.KEYWORD,
            )

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return
        self._create_collection()

    def reset_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            self._client.delete_collection(self._collection_name)
        self._create_collection()

    def upsert_chunks(
        self,
        chunks: Sequence[CvChunkPayload],
        dense_vectors: Sequence[Sequence[float]],
        sparse_vectors: Sequence[SparseVector],
    ) -> None:
        points = [
            PointStruct(
                id=chunk.point_id,
                vector={
                    DENSE_VECTOR_NAME: list(dense_vector),
                    SPARSE_VECTOR_NAME: sparse_vector,
                },
                payload=chunk.model_dump(mode="json", exclude={"point_id"}),
            )
            for chunk, dense_vector, sparse_vector in zip(
                chunks,
                dense_vectors,
                sparse_vectors,
                strict=True,
            )
        ]
        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )

    @staticmethod
    def _build_search_filter(
        chunk_types: Sequence[CvChunkType] | None,
        profile_id: str | None,
    ) -> Filter | None:
        conditions: list[FieldCondition] = []
        if chunk_types:
            conditions.append(
                FieldCondition(
                    key="chunk_type",
                    match=MatchAny(
                        any=[chunk_type.value for chunk_type in chunk_types]
                    ),
                ),
            )
        if profile_id is not None:
            conditions.append(
                FieldCondition(
                    key="profile_id",
                    match=MatchValue(value=profile_id),
                ),
            )
        if not conditions:
            return None
        return Filter(must=cast(list[Condition], conditions))

    def search(
        self,
        *,
        dense_vector: Sequence[float],
        sparse_vector: SparseVector,
        chunk_types: Sequence[CvChunkType] | None,
        profile_id: str | None,
        limit: int,
    ) -> list[ScoredPoint]:
        if not self._client.collection_exists(self._collection_name):
            return []

        query_filter = self._build_search_filter(chunk_types, profile_id)
        prefetch_limit = min(max(limit * 2, 10), 100)
        response = self._client.query_points(
            collection_name=self._collection_name,
            prefetch=[
                Prefetch(
                    query=list(dense_vector),
                    using=DENSE_VECTOR_NAME,
                    filter=query_filter,
                    limit=prefetch_limit,
                ),
                Prefetch(
                    query=sparse_vector,
                    using=SPARSE_VECTOR_NAME,
                    filter=query_filter,
                    limit=prefetch_limit,
                ),
            ],
            # query=FusionQuery(fusion=Fusion.RRF),
            query=RrfQuery(
                rrf=Rrf(
                    k=60,
                    weights=[1.0, 2.0],  # dense, sparse
                )
            ),
            limit=limit,
            with_payload=True,
        )
        return list(response.points)
