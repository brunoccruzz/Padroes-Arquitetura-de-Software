from datetime import datetime

from src.interfaces import OrderRepositoryInterface
from src.models import CustomerType, Order, OrderItem, OrderStatus
from src.strategies.discount_strategy import DiscountStrategyResolverInterface


class OrderService:
    def __init__(
        self,
        repository: OrderRepositoryInterface,
        discount_resolver: DiscountStrategyResolverInterface,
    ) -> None:
        self.repository = repository
        self.discount_resolver = discount_resolver

    def create_order(self, customer_name: str, customer_type: str, items: list[dict]) -> Order:
        if not items:
            raise ValueError("order must have at least one item")

        parsed_customer_type = CustomerType(customer_type.upper())
        order_items = self._build_items(items)
        subtotal = round(sum(item.line_total for item in order_items), 2)
        discount = self.discount_resolver.resolve(parsed_customer_type).calculate(subtotal)
        total = round(subtotal - discount, 2)
        order = Order(
            id=None,
            customer_name=customer_name,
            customer_type=parsed_customer_type,
            subtotal=subtotal,
            discount=discount,
            total=total,
            status=OrderStatus.CREATED,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            items=order_items,
        )
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

    def _build_items(self, items: list[dict]) -> list[OrderItem]:
        order_items = []
        for item in items:
            quantity = int(item["quantity"])
            unit_price = float(item["unit_price"])
            order_items.append(
                OrderItem(
                    sku=item["sku"],
                    name=item["name"],
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=round(quantity * unit_price, 2),
                )
            )
        return order_items
