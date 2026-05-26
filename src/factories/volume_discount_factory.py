from src.factories.order_factory import OrderItemInput, OrderItemsInput, PedidoFactoryInterface
from src.models import Order


class VolumeDiscountPedidoFactory(PedidoFactoryInterface):
    """Decorator: applies 15% discount on items with quantity >= 3 before delegating."""

    _THRESHOLD: int = 3
    _RATE: float = 0.15

    def __init__(self, inner: PedidoFactoryInterface) -> None:
        self._inner = inner

    def create_order(self, customer_name: str, customer_type: str, items: OrderItemsInput) -> Order:
        adjusted = self._apply_volume_discount(items)
        return self._inner.create_order(customer_name, customer_type, adjusted)

    def _apply_volume_discount(self, items: OrderItemsInput) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for item in items:
            quantity = self._to_int(item, "quantity")
            if quantity >= self._THRESHOLD:
                unit_price = self._to_float(item, "unit_price")
                adjusted: dict[str, object] = dict(item)
                adjusted["unit_price"] = round(unit_price * (1.0 - self._RATE), 2)
                result.append(adjusted)
            else:
                result.append(dict(item))
        return result

    @staticmethod
    def _to_int(item: OrderItemInput, key: str) -> int:
        value = item[key]
        if isinstance(value, int):
            return value
        if isinstance(value, float | str):
            return int(value)
        raise TypeError(f"{key} must be numeric")

    @staticmethod
    def _to_float(item: OrderItemInput, key: str) -> float:
        value = item[key]
        if isinstance(value, float | int):
            return float(value)
        if isinstance(value, str):
            return float(value)
        raise TypeError(f"{key} must be numeric")
