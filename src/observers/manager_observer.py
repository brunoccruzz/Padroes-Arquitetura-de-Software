from src.interfaces import NotificationObserverInterface
from src.models import CustomerType, Order


class ManagerNotificationObserver(NotificationObserverInterface):
    """Sends manager notifications for CORPORATE profiles."""

    def update(self, order: Order) -> None:
        if order.customer_type == CustomerType.CORPORATE:
            pass
