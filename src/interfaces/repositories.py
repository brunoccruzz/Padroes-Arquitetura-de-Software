from abc import ABC, abstractmethod

from src.models import Order, OrderStatus, PaymentRecord


class OrderRepositoryInterface(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, order_id: int) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    def add_payment(self, order_id: int, payment: PaymentRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, order_id: int, status: OrderStatus) -> bool:
        raise NotImplementedError

    @abstractmethod
    def report_summary(self) -> tuple[int, float, dict[str, int], dict[str, int]]:
        raise NotImplementedError
