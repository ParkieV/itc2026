from dataclasses import replace

import pandas as pd

from entities.comment import Comment
from entities.comment_status import CommentStatus
from utils.datetime_iso import from_unix_seconds_iso_msk


class AsyncInMemoryCommentsRepository:
    def __init__(self):
        self._rows = pd.DataFrame(
            [
                {
                    "comment_id": 1,
                    "doc_id": 1,
                    "stage_id": 1,
                    "user_id": 1,
                    "reply_to": pd.NA,
                    "remark": "Initial review",
                    "proposal": "Please fix formatting and naming.",
                    "justification": pd.NA,
                    "developer_response": pd.NA,
                    "xfdf": "",
                    "status": pd.NA,
                    "is_viewed": False,
                    "created_at": from_unix_seconds_iso_msk(1710000000),
                },
                {
                    "comment_id": 2,
                    "doc_id": 1,
                    "stage_id": 1,
                    "user_id": 2,
                    "reply_to": 1,
                    "remark": "LGTM",
                    "proposal": "No additional comments.",
                    "justification": pd.NA,
                    "developer_response": pd.NA,
                    "xfdf": "",
                    "status": pd.NA,
                    "is_viewed": False,
                    "created_at": from_unix_seconds_iso_msk(1710003600),
                },
                {
                    "comment_id": 3,
                    "doc_id": 2,
                    "stage_id": 2,
                    "user_id": 1,
                    "reply_to": pd.NA,
                    "remark": "Needs tests",
                    "proposal": "Please add integration tests.",
                    "justification": pd.NA,
                    "developer_response": pd.NA,
                    "xfdf": "",
                    "status": pd.NA,
                    "is_viewed": False,
                    "created_at": from_unix_seconds_iso_msk(1710007200),
                },
            ]
        )
        self._next_id = int(self._rows["comment_id"].max()) + 1

    @property
    def rows(self) -> pd.DataFrame:
        return self._rows.copy()

    @staticmethod
    def _reply_to_value(v) -> int | None:
        if v is None or pd.isna(v):
            return None
        return int(v)

    @staticmethod
    def _status_value(v) -> CommentStatus | None:
        if v is None or pd.isna(v):
            return None
        s = str(v).strip()
        if not s:
            return None
        return CommentStatus(s)

    @staticmethod
    def _nullable_str_value(v) -> str | None:
        if v is None or pd.isna(v):
            return None
        s = str(v)
        if not s.strip():
            return None
        return s

    def _series_to_comment(self, row: pd.Series) -> Comment:
        return Comment(
            comment_id=int(row["comment_id"]),
            doc_id=int(row["doc_id"]),
            stage_id=int(row["stage_id"]),
            user_id=int(row["user_id"]),
            remark=self._nullable_str_value(row["remark"]),
            proposal=self._nullable_str_value(row["proposal"]),
            justification=self._nullable_str_value(row["justification"]),
            developer_response=self._nullable_str_value(row["developer_response"]),
            xfdf=str(row["xfdf"]),
            created_at=str(row["created_at"]),
            reply_to=self._reply_to_value(row["reply_to"]),
            status=self._status_value(row["status"]),
            is_viewed=bool(row["is_viewed"]),
        )

    async def add(self, comment: Comment) -> Comment:
        new_id = self._next_id
        self._next_id += 1
        stored = replace(comment, comment_id=new_id)
        self._rows.loc[len(self._rows)] = {
            "comment_id": stored.comment_id,
            "doc_id": stored.doc_id,
            "stage_id": stored.stage_id,
            "user_id": stored.user_id,
            "reply_to": pd.NA if stored.reply_to is None else stored.reply_to,
            "remark": pd.NA if stored.remark is None else stored.remark,
            "proposal": pd.NA if stored.proposal is None else stored.proposal,
            "justification": pd.NA if stored.justification is None else stored.justification,
            "developer_response": pd.NA if stored.developer_response is None else stored.developer_response,
            "xfdf": stored.xfdf,
            "status": pd.NA if stored.status is None else stored.status.value,
            "is_viewed": stored.is_viewed,
            "created_at": stored.created_at,
        }
        return stored

    async def get_by_doc_and_comment_id(self, doc_id: int, comment_id: int) -> Comment | None:
        filtered = self.rows[
            (self.rows["doc_id"] == doc_id) & (self.rows["comment_id"] == comment_id)
        ]
        if filtered.empty:
            return None
        return self._series_to_comment(filtered.iloc[0])

    async def get_by_doc_and_stage_id(self, doc_id: int, stage_id: int) -> list[Comment]:
        filtered = self.rows[
            (self.rows["doc_id"] == doc_id)
            & (self.rows["stage_id"] == stage_id)
        ]
        return [self._series_to_comment(filtered.loc[idx]) for idx in filtered.index]

    async def get_by_doc_id(self, doc_id: int) -> list[Comment]:
        filtered = self.rows[self.rows["doc_id"] == doc_id]
        return [self._series_to_comment(filtered.loc[idx]) for idx in filtered.index]

    async def update_is_viewed_and_status(
        self,
        doc_id: int,
        comment_id: int,
        *,
        is_viewed: bool | None = None,
        status: CommentStatus | None = None,
    ) -> Comment | None:
        mask = (self._rows["doc_id"] == doc_id) & (self._rows["comment_id"] == comment_id)
        matching = self._rows.index[mask]
        if len(matching) == 0:
            return None
        idx = matching[0]
        if is_viewed is not None:
            self._rows.at[idx, "is_viewed"] = is_viewed
        if status is not None:
            self._rows.at[idx, "status"] = status.value
        return self._series_to_comment(self._rows.loc[idx])
