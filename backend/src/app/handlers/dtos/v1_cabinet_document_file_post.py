from pydantic import BaseModel, Field


class V1CabinetDocumentFilePostResponse200(BaseModel):
    document_id: int = Field(description="Идентификатор созданного документа")
    file_id: int = Field(description="Идентификатор файла документа")
    pdf_file_id: int = Field(description="Идентификатор PDF-файла документа")


class V1CabinetDocumentFilePostResponse400(BaseModel):
    detail: str = Field(description="Текст ошибки валидации запроса")


class V1CabinetDocumentFilePostResponse403(BaseModel):
    detail: str = Field(description="Текст ошибки доступа")


class V1CabinetDocumentFilePostResponse404(BaseModel):
    detail: str = Field(description="Связанная сущность не найдена")
