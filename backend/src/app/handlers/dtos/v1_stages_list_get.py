from __future__ import annotations

from dataclasses import field
from typing import Any

from pydantic import BaseModel, Field, RootModel

from entities.document_user_status import DocumentUserStatus


class StageGetResponse(BaseModel):
    stage_id: int
    next_stage: int
    title: str
    docs: list[Any] = field(default_factory=list)
    reviewers: list[Any] = field(default_factory=list)


class StageSummaryGetResponse(BaseModel):
    stage_id: int
    next_stage: int
    title: str


class StageReviewerUserGetResponse(BaseModel):
    user_id: str
    fio: str


class UserPreview(BaseModel):
    id: int
    fio: str


class DocumentGetResponse(BaseModel):
    doc_id: int
    title: str
    description: str
    authors: list[UserPreview]
    created_at: str
    modified_at: str
    status: DocumentUserStatus | None = Field(
        default=None,
        description="Статус документа для текущего пользователя; null, если не автор и не ревьюер.",
    )


class V1StageWithReviewerAndDocsGetResponse(BaseModel):
    stage: StageSummaryGetResponse
    docs: list[DocumentGetResponse] = Field(default_factory=list)
    reviewers: list[StageReviewerUserGetResponse] = Field(default_factory=list)


class V1_STAGES_LIST_GET_RESPONSE200(RootModel[list[V1StageWithReviewerAndDocsGetResponse]]):
    """Список этапов с документами и ревьюерами."""


class V1_STAGES_LIST_GET_RESPONSE401(BaseModel):
    """Невалидный JWT или в токене нет subject (sub)."""

    detail: str = Field(description="Текст ошибки")
