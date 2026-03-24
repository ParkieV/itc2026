from entities.document import Document
from entities.stage_with_reviewer_and_docs import StageWithReviewerAndDocs
from entities.user import User
from repositories.inmemory_document_repo import InMemoryDocumentRepository
from repositories.inmemory_stage_reviewers_repo import AsyncInMemoryStageReviewersRepository
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from repositories.inmemory_user_repo import AsyncInMemoryUserRepository


class GetStagesWithReviewerAndDocsUseCase:
    def __init__(
        self,
        stages_repo: AsyncInMemoryStagesRepository,
        document_repo: InMemoryDocumentRepository,
        stage_reviewers_repo: AsyncInMemoryStageReviewersRepository,
        user_repo: AsyncInMemoryUserRepository,
    ):
        self._stages_repo = stages_repo
        self._document_repo = document_repo
        self._stage_reviewers_repo = stage_reviewers_repo
        self._user_repo = user_repo

    async def execute(self) -> list[StageWithReviewerAndDocs]:
        stages = await self._stages_repo.list_all()
        documents = self._document_repo.get_list()
        stage_reviewers = await self._stage_reviewers_repo.get_list()

        docs_by_stage: dict[int, list[Document]] = {}
        for doc in documents:
            docs_by_stage.setdefault(doc.stage_id, []).append(doc)

        reviewer_ids_by_stage: dict[int, list[int]] = {}
        for link in stage_reviewers:
            reviewer_ids_by_stage.setdefault(link.stage_id, []).append(link.reviewer_id)

        out: list[StageWithReviewerAndDocs] = []
        for stage in stages:
            docs = docs_by_stage.get(stage.stage_id, [])
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
