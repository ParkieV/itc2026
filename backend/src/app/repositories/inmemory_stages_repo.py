import pandas as pd

from entities.stage import Stage
from repositories.stage_exceptions import StageNotFound


class AsyncInMemoryStagesRepository:
    def __init__(self):
        self._stages = pd.DataFrame(
            [
                {"stage_id": 1, "next_stage": 2, "title": "предварительная проверка"},
                {"stage_id": 2, "next_stage": 3, "title": "экспертная оценка"},
                {"stage_id": 3, "next_stage": 4, "title": "доработка"},
                {"stage_id": 4, "next_stage": None, "title": "утверждён"},
            ]
        ).set_index("stage_id")

    @property
    def stages(self) -> pd.DataFrame:
        return self._stages.copy()

    @staticmethod
    def _next_stage_value(v) -> int | None:
        if v is None or pd.isna(v):
            return None
        return int(v)

    async def list_all(self) -> list[Stage]:
        df = self.stages.reset_index()
        return [
            Stage(
                stage_id=int(row["stage_id"]),
                next_stage=self._next_stage_value(row["next_stage"]),
                title=str(row["title"]),
            )
            for _, row in df.iterrows()
        ]

    async def get_by_id(self, stage_id: int) -> Stage | None:
        try:
            row = self.stages.loc[stage_id]
        except KeyError:
            return None

        return Stage(
            stage_id=int(row.name),
            next_stage=self._next_stage_value(row["next_stage"]),
            title=str(row["title"]),
        )
