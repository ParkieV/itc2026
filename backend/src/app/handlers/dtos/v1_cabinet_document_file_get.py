from pydantic import BaseModel, Field


class V1_CABINET_DOCUMENT_FILE_GET_RESPONSE200:
    """Файл документа; тело — бинарный поток (chunked), поддерживаются Range-запросы.

    Content-Type по расширению или application/octet-stream.
    """


class V1_CABINET_DOCUMENT_FILE_GET_RESPONSE403(BaseModel):
    """Текущий пользователь не входит в авторы документа."""

    detail: str = Field(description="Текст ошибки")


class V1_CABINET_DOCUMENT_FILE_GET_RESPONSE404(BaseModel):
    """Документ не найден, путь к файлу пустой или файл отсутствует на диске."""

    detail: str = Field(description="Текст ошибки")
