from typing import List

from entities.stage import Stage
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository


class GetStagesService:
    def __init__(self, stages_repo: AsyncInMemoryStagesRepository):
        self._stages_repo = stages_repo

    async def execute(self) -> List[Stage]:
        stages = await self._stages_repo.list_all()
        return stages