from pydantic import BaseModel


class CommentAuthorPreview(BaseModel):
    user_id: int
    fio: str
    organization: str
    phone: str
    email: str
