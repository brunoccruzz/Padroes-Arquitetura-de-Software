from src.factories import OrderItemsInput, PedidoFactoryInterface
from src.interfaces import OrderRepositoryInterface
from src.models import Order, OrderStatus


class OrderService:
    def __init__(
        self,
        repository: OrderRepositoryInterface,
        order_factory: PedidoFactoryInterface,
    ) -> None:
        self.repository = repository
        self.order_factory = order_factory

    def create_order(
        self,
        customer_name: str,
        customer_type: str,
        items: OrderItemsInput,
    ) -> Order:
        if not items:
            raise ValueError("order must have at least one item")

        order = self.order_factory.create_order(customer_name, customer_type, items)
        return self.repository.save(order)

    def get_order(self, order_id: int) -> Order | None:
        return self.repository.get_by_id(order_id)

    def update_status(self, order_id: int, status: str) -> Order:
        changed = self.repository.update_status(order_id, OrderStatus(status.upper()))
        if not changed:
            raise ValueError("order not found")
        order = self.repository.get_by_id(order_id)
        if order is None:
            raise ValueError("order not found")
        return order

    def cancel_order(self, order_id: int) -> Order:
        order = self.repository.get_by_id(order_id)
        if order is None:
            raise ValueError("order not found")
        if order.status == OrderStatus.PAID:
            raise ValueError("paid orders cannot be cancelled")
        return self.update_status(order_id, OrderStatus.CANCELLED.value)
