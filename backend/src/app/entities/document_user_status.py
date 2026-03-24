from enum import StrEnum


class DocumentUserStatus(StrEnum):
    NEW_COMMENT = "new_comment"
    NOT_VIEWED = "not_viewed"
    VIEWED = "viewed"
    WAITING = "waiting"
    ACTION_REQUIRED = "action_required"
    SENT = "sent"
