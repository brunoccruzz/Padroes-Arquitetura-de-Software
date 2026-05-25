from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from datetime import datetime

from src.models import CustomerType, Order, OrderItem, OrderStatus
from src.strategies.discount_strategy import DiscountStrategyResolverInterface

OrderItemInput = Mapping[str, object]
OrderItemsInput = Sequence[OrderItemInput]
ScalarInput = str | int | float


class OrderFactoryInterface(ABC):
    @abstractmethod
    def create(self, customer_name: str, items: OrderItemsInput) -> Order:
        raise NotImplementedError


class PedidoFactoryInterface(ABC):
    @abstractmethod
    def create_order(
        self,
        customer_name: str,
        customer_type: str,
        items: OrderItemsInput,
    ) -> Order:
        raise NotImplementedError


class CustomerOrderFactory(OrderFactoryInterface):
    def __init__(
        self,
        customer_type: CustomerType,
        discount_resolver: DiscountStrategyResolverInterface,
    ) -> None:
        self._customer_type = customer_type
        self._discount_resolver = discount_resolver

    def create(self, customer_name: str, items: OrderItemsInput) -> Order:
        order_items = self._build_items(items)
        subtotal = round(sum(item.line_total for item in order_items), 2)
        discount = self._discount_resolver.resolve(self._customer_type).calculate(subtotal)
        total = round(subtotal - discount, 2)
        return Order(
            id=None,
            customer_name=customer_name,
            customer_type=self._customer_type,
            subtotal=subtotal,
            discount=discount,
            total=total,
            status=OrderStatus.CREATED,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            items=order_items,
        )

    def _build_items(self, items: OrderItemsInput) -> list[OrderItem]:
        order_items: list[OrderItem] = []
        for item in items:
            quantity = int(self._required_scalar(item, "quantity"))
            unit_price = float(self._required_scalar(item, "unit_price"))
            order_items.append(
                OrderItem(
                    sku=str(item["sku"]),
                    name=str(item["name"]),
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=round(quantity * unit_price, 2),
                )
            )
        return order_items

    def _required_scalar(self, item: OrderItemInput, key: str) -> ScalarInput:
        value = item[key]
        if isinstance(value, str | int | float):
            return value
        raise TypeError(f"{key} must be str, int or float")


class NormalOrderFactory(CustomerOrderFactory):
    def __init__(self, discount_resolver: DiscountStrategyResolverInterface) -> None:
        super().__init__(CustomerType.NORMAL, discount_resolver)


class VipOrderFactory(CustomerOrderFactory):
    def __init__(self, discount_resolver: DiscountStrategyResolverInterface) -> None:
        super().__init__(CustomerType.VIP, discount_resolver)


class CorporateOrderFactory(CustomerOrderFactory):
    def __init__(self, discount_resolver: DiscountStrategyResolverInterface) -> None:
        super().__init__(CustomerType.CORPORATE, discount_resolver)


class PedidoFactory(PedidoFactoryInterface):
    def __init__(
        self,
        factories: Mapping[CustomerType, OrderFactoryInterface],
    ) -> None:
        self._factories = dict(factories)

    @classmethod
    def from_discount_resolver(
        cls,
        discount_resolver: DiscountStrategyResolverInterface,
    ) -> "PedidoFactory":
        return cls(
            {
                CustomerType.NORMAL: NormalOrderFactory(discount_resolver),
                CustomerType.VIP: VipOrderFactory(discount_resolver),
                CustomerType.CORPORATE: CorporateOrderFactory(discount_resolver),
            }
        )

    def create_order(
        self,
        customer_name: str,
        customer_type: str,
        items: OrderItemsInput,
    ) -> Order:
        parsed_customer_type = CustomerType(customer_type.upper())
        return self._factories[parsed_customer_type].create(customer_name, items)
