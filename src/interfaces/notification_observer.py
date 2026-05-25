from abc import ABC, abstractmethod

from src.models import Order


class NotificationObserverInterface(ABC):
    @abstractmethod
    def update(self, order: Order) -> None:
        raise NotImplementedError
