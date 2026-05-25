from src.interfaces import NotificationObserverInterface
from src.models import Order


class EmailNotificationObserver(NotificationObserverInterface):
    """Sends email notifications for all profiles."""

    def update(self, order: Order) -> None:
        # Email is sent to all profiles.
        pass
