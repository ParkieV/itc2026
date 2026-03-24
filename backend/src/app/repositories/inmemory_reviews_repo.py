import pandas as pd

from entities.review import Review
from entities.review_status import ReviewStatus


class AsyncInMemoryReviewsRepository:
    def __init__(self):
        self._rows = pd.DataFrame(
            [
                {
                    "stage_id": 1,
                    "doc_id": 1,
                    "user_id": 1,
                    "status": pd.NA,
                    "is_viewed": False,
                },
                {
                    "stage_id": 1,
                    "doc_id": 1,
                    "user_id": 2,
                    "status": pd.NA,
                    "is_viewed": False,
                },
                {
                    "stage_id": 2,
                    "doc_id": 2,
                    "user_id": 2,
                    "status": pd.NA,
                    "is_viewed": False,
                },
            ]
        )

    @property
    def rows(self) -> pd.DataFrame:
        return self._rows.copy()

    @staticmethod
    def _status_value(v) -> ReviewStatus | None:
        if v is None or pd.isna(v):
            return None
        s = str(v).strip()
        if not s:
            return None
        return ReviewStatus(s)

    def _row_to_review(self, row) -> Review:
        return Review(
            stage_id=int(row["stage_id"]),
            doc_id=int(row["doc_id"]),
            user_id=int(row["user_id"]),
            is_viewed=bool(row["is_viewed"]),
            status=self._status_value(row["status"]),
        )

    async def get_all(self) -> list[Review]:
        return [self._row_to_review(row) for _, row in self.rows.iterrows()]

    async def add(self, review: Review) -> None:
        self._rows.loc[len(self._rows)] = {
            "stage_id": review.stage_id,
            "doc_id": review.doc_id,
            "user_id": review.user_id,
            "status": pd.NA if review.status is None else review.status.value,
            "is_viewed": review.is_viewed,
        }

    async def get_list_by_stage_and_doc(self, stage_id: int, doc_id: int) -> list[Review]:
        filtered = self.rows[
            (self.rows["stage_id"] == stage_id)
            & (self.rows["doc_id"] == doc_id)
        ]
        return [self._row_to_review(row) for _, row in filtered.iterrows()]

    async def get_list_by_user_id(self, user_id: int) -> list[Review]:
        filtered = self.rows[self.rows["user_id"] == user_id]
        return [self._row_to_review(row) for _, row in filtered.iterrows()]

    async def update_view_status(
        self,
        stage_id: int,
        doc_id: int,
        user_id: int,
        is_viewed: bool,
    ) -> int:
        mask = (
            (self._rows["stage_id"] == stage_id)
            & (self._rows["doc_id"] == doc_id)
            & (self._rows["user_id"] == user_id)
        )
        self._rows.loc[mask, "is_viewed"] = is_viewed
        return int(mask.sum())

    async def update_status(
        self,
        stage_id: int,
        doc_id: int,
        user_id: int,
        status: ReviewStatus,
    ) -> int:
        mask = (
            (self._rows["stage_id"] == stage_id)
            & (self._rows["doc_id"] == doc_id)
            & (self._rows["user_id"] == user_id)
        )
        self._rows.loc[mask, "status"] = status.value
        return int(mask.sum())

    async def delete(self, stage_id: int, doc_id: int, user_id: int) -> int:
        mask = (
            (self._rows["stage_id"] == stage_id)
            & (self._rows["doc_id"] == doc_id)
            & (self._rows["user_id"] == user_id)
        )
        deleted_count = int(mask.sum())
        self._rows = self._rows.loc[~mask].reset_index(drop=True)
        return deleted_count
