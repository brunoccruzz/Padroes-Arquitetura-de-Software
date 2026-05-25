from src.interfaces import NotificationObserverInterface
from src.models import Order


class WhatsAppNotificationObserver(NotificationObserverInterface):
    """Sends WhatsApp notifications for all profiles (Extensão 2)."""

    def update(self, order: Order) -> None:
        # WhatsApp is sent to all profiles
        pass
