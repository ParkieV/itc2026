class UserNotificationNotFound(Exception):
    """Уведомление не найдено или принадлежит другому пользователю."""

    def __str__(self) -> str:
        return "notification_not_found"
