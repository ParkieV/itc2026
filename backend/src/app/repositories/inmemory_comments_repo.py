import pandas as pd

from entities.comment import Comment


class AsyncInMemoryCommentsRepository:
    def __init__(self):
        self._rows = pd.DataFrame(
            [
                {
                    "doc_id": 1,
                    "stage_id": 1,
                    "user_id": 1,
                    "subject": "Initial review",
                    "content": "Please fix formatting and naming.",
                    "created_at": 1710000000,
                },
                {
                    "doc_id": 1,
                    "stage_id": 1,
                    "user_id": 2,
                    "subject": "LGTM",
                    "content": "No additional comments.",
                    "created_at": 1710003600,
                },
                {
                    "doc_id": 2,
                    "stage_id": 2,
                    "user_id": 1,
                    "subject": "Needs tests",
                    "content": "Please add integration tests.",
                    "created_at": 1710007200,
                },
            ]
        )

    @property
    def rows(self) -> pd.DataFrame:
        return self._rows.copy()

    async def add(self, comment: Comment) -> None:
        self._rows.loc[len(self._rows)] = {
            "doc_id": comment.doc_id,
            "stage_id": comment.stage_id,
            "user_id": comment.user_id,
            "subject": comment.subject,
            "content": comment.content,
            "created_at": comment.created_at,
        }

    async def get_by_doc_and_stage_id(self, doc_id: int, stage_id: int) -> list[Comment]:
        filtered = self.rows[
            (self.rows["doc_id"] == doc_id)
            & (self.rows["stage_id"] == stage_id)
        ]
        return [
            Comment(
                doc_id=int(row["doc_id"]),
                stage_id=int(row["stage_id"]),
                user_id=int(row["user_id"]),
                subject=str(row["subject"]),
                content=str(row["content"]),
                created_at=int(row["created_at"]),
            )
            for _, row in filtered.iterrows()
        ]

    async def get_by_doc_id(self, doc_id: int) -> list[Comment]:
        filtered = self.rows[self.rows["doc_id"] == doc_id]
        return [
            Comment(
                doc_id=int(row["doc_id"]),
                stage_id=int(row["stage_id"]),
                user_id=int(row["user_id"]),
                subject=str(row["subject"]),
                content=str(row["content"]),
                created_at=int(row["created_at"]),
            )
            for _, row in filtered.iterrows()
        ]
