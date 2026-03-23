from dataclasses import field
from typing import Any

from pydantic import BaseModel, Field


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


class V1StageWithReviewerAndDocsGetResponse(BaseModel):
    stage: StageSummaryGetResponse
    docs: list[Any] = Field(default_factory=list)
    reviewers: list[StageReviewerUserGetResponse] = Field(default_factory=list)
