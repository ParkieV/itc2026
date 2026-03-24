from entities import Document
from services.add_document.exceptions import InvalidAuthorId
from services.add_document.service import AddDocumentService
from services.authenticate_user.exceptions import UserNotFound
from services.get_user.service import GetUserService


class AddDocumentUseCase:
    def __init__(
            self,
            get_user_service: GetUserService,
            add_document_service: AddDocumentService,
    ):
        self._get_user_service = get_user_service
        self._add_document_service = add_document_service

    async def execute(self, document: Document) -> None:
        for author_id in document.authors:
            try:
                await self._get_user_service.execute(author_id)
            except UserNotFound as err:
                raise InvalidAuthorId(str(err)) from err

        await self._add_document_service.execute(document)
