from typing import Literal

from entities.stage_with_reviewer_and_docs import StageWithReviewerAndDocs
from entities.user import User
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from repositories.inmemory_reviews_repo import AsyncInMemoryReviewsRepository
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository
from services.filter_documents.service import FilterDocumentsService


class GetStagesWithReviewerAndDocsUseCase:
    def __init__(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
        document_repo: InMemoryDocumentRepository,
        reviews_repo: AsyncInMemoryReviewsRepository,
        user_repo: AsyncInMemoryUserRepository,
        filter_documents_service: FilterDocumentsService,
    ):
        self._stages_repo = stages_repo
        self._document_repo = document_repo
        self._reviews_repo = reviews_repo
        self._user_repo = user_repo
        self._filter_documents_service = filter_documents_service

    async def execute(
        self,
        author_id: int,
        roles: list[Literal['author', 'reviewer']] | None = None,
        review_statuses: list[Literal['accepted', 'declined']] | None = None,
        categories: list[str] | None = None,
        doc_statuses: list[Literal['new_comment', 'not_viewed', 'viewed', 'waiting', 'action_required', 'sent']] | None = None,
    ) -> list[StageWithReviewerAndDocs]:
        stages = await self._stages_repo.list_all()
        reviews = await self._reviews_repo.get_all()

        reviewer_ids_by_stage: dict[int, list[int]] = {}
        for review in reviews:
            reviewer_ids_by_stage.setdefault(review.stage_id, []).append(review.user_id)

        out: list[StageWithReviewerAndDocs] = []
        for stage in stages:
            docs = await self._filter_documents_service.execute(
                author_id=author_id,
                stage_id=stage.stage_id,
                roles=roles,
                review_statuses=review_statuses,
                categories=categories,
                doc_statuses=doc_statuses,
                ) or list()
            if roles is not None and 'reviewer' in roles:
                docs = [doc for doc in docs if author_id in reviewer_ids_by_stage.get(stage.stage_id, [])]
            reviewer_ids = reviewer_ids_by_stage.get(stage.stage_id, [])
            reviewers: list[User] = []
            for rid in reviewer_ids:
                user = await self._user_repo.get_by_id(rid)
                if user is not None:
                    reviewers.append(user)

            out.append(
                StageWithReviewerAndDocs(
                    stage=stage,
                    docs=docs,
                    reviewers=reviewers,
                )
            )
        return out
