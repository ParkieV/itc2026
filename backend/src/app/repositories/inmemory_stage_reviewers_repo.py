import pandas as pd

from entities.stage_reviewer import StageReviewer


class AsyncInMemoryStageReviewersRepository:
    def __init__(self):
        self._rows = pd.DataFrame(
            [
                {"reviewer_id": 1, "stage_id": 1},
                {"reviewer_id": 2, "stage_id": 1},
                {"reviewer_id": 3, "stage_id": 2},
            ]
        )

    @property
    def rows(self) -> pd.DataFrame:
        return self._rows.copy()

    async def get_list(self, reviewer_ids: list[int] | None = None) -> list[StageReviewer]:
        df = self.rows
        if reviewer_ids:
            df = df[df["reviewer_id"].isin(reviewer_ids)]
        return [
            StageReviewer(
                reviewer_id=int(row["reviewer_id"]),
                stage_id=int(row["stage_id"]),
            )
            for _, row in df.iterrows()
        ]
