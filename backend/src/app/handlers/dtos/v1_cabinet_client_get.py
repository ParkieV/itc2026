from pydantic import BaseModel


class V1CabinetClientGetResponse(BaseModel):
    fio: str
    login: str
