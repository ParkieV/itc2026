from entities.stage import Stage
from repositories.inmemory_stages_repo import AsyncInMemoryStagesRepository
from .exceptions import StageNotFound


class GetStageByIdService:
    def __init__(self, stages_repo: AsyncInMemoryStagesRepository):
        self._stages_repo = stages_repo

    async def execute(self, stage_id: int) -> Stage:
        stage = await self._stages_repo.get_by_id(stage_id)
        if stage is None:
            raise StageNotFound(f"stage with id={stage_id} not found")
        return stage
