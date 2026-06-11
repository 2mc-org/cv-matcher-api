"""Dense and sparse text embeddings for CV chunk ingest and search."""

from __future__ import annotations

from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client.models import SparseVector

from app.core.environments import environments


class CvEmbeddingService:
    """Thin wrapper around fastembed dense + sparse models for CV chunk text."""

    def __init__(self) -> None:
        self._dense_model = TextEmbedding(
            model_name=environments.CV_EMBEDDING_MODEL
        )
        self._sparse_model = SparseTextEmbedding(
            model_name=environments.CV_SPARSE_EMBEDDING_MODEL,
        )

    @property
    def dense_vector_size(self) -> int:
        return self._dense_model.embedding_size

    def embed_dense_texts(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._dense_model.embed(texts)]

    def embed_sparse_texts(self, texts: list[str]) -> list[SparseVector]:
        return [
            SparseVector(
                indices=embedding.indices.tolist(),
                values=embedding.values.tolist(),
            )
            for embedding in self._sparse_model.embed(texts)
        ]
