class CommentNotFound(Exception):
    def __init__(self, doc_id: int, comment_id: int) -> None:
        self.doc_id = doc_id
        self.comment_id = comment_id
        super().__init__(f"Comment {comment_id} for document {doc_id} not found")
