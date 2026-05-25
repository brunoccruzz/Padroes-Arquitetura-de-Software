from src.interfaces import NotificationObserverInterface
from src.models import CustomerType, Order


class SmsNotificationObserver(NotificationObserverInterface):
    """Sends SMS notifications for VIP profiles."""

    def update(self, order: Order) -> None:
        if order.customer_type == CustomerType.VIP:
            pass
