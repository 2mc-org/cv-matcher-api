"""Hybrid CV search over Qdrant chunk points."""

from __future__ import annotations

import logging
from collections import defaultdict

from app.cv.models.cv_chunk import CV_CHUNK_PAYLOAD_ADAPTER
from app.cv.models.cv_search_hit import CvSearchHit, CvSearchProfileResult
from app.cv.models.cv_search_request import CvSearchRequest
from app.cv.services.cv_embedding_service import CvEmbeddingService
from app.cv.services.cv_qdrant_repository import CvQdrantRepository


class CvSearchService:
    """Embed queries and run hybrid dense + sparse search grouped by profile."""

    def __init__(
        self,
        embedding_service: CvEmbeddingService,
        qdrant_repository: CvQdrantRepository,
    ) -> None:
        self._embedding = embedding_service
        self._qdrant = qdrant_repository
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def search(self, request: CvSearchRequest) -> list[CvSearchProfileResult]:
        dense_vector = self._embedding.embed_dense_texts([request.query])[0]
        sparse_vector = self._embedding.embed_sparse_texts([request.query])[0]

        scored_points = self._qdrant.search(
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
            chunk_types=request.chunk_types,
            profile_id=request.profile_id,
            limit=request.chunk_limit,
        )
        if not scored_points:
            return []

        hits_by_profile = defaultdict(list[CvSearchHit])
        profile_names: dict[str, str] = {}

        for point in scored_points:
            if point.payload is None or point.score is None:
                continue

            payload = CV_CHUNK_PAYLOAD_ADAPTER.validate_python(point.payload)
            hits_by_profile[payload.profile_id].append(
                CvSearchHit(fusion_score=point.score, payload=payload),
            )
            profile_names[payload.profile_id] = payload.full_name

        results = [
            CvSearchProfileResult(
                profile_id=profile_id,
                full_name=profile_names[profile_id],
                fusion_score=max(hit.fusion_score for hit in hits),
                hits=sorted(
                    hits, key=lambda hit: hit.fusion_score, reverse=True
                ),
            )
            for profile_id, hits in hits_by_profile.items()
        ]
        results.sort(key=lambda result: result.fusion_score, reverse=True)

        self.logger.info(
            "Search %r returned %s profiles from %s chunk hits",
            request.query,
            len(results),
            len(scored_points),
        )
        return results
