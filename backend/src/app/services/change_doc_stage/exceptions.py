class StageNotFound(Exception):
    pass


class DocumentNotFound(Exception):
    pass


class InvalidTargetStage(Exception):
    pass


class ReviewsNotAllAccepted(Exception):
    """Не все ревьюеры на текущем этапе выставили статус ACCEPTED."""

    pass


class DocumentRevisionRequired(Exception):
    """Есть отклонения ревью — нужно внести правки в документ."""

    pass
