import pytest

from src.factories import (
    CorporateOrderFactory,
    NormalOrderFactory,
    OrderFactoryInterface,
    PedidoFactory,
    VipOrderFactory,
)
from src.models import CustomerType, OrderStatus
from src.strategies.discount_strategy import (
    CorporateDiscountStrategy,
    DefaultDiscountStrategyResolver,
    NoDiscountStrategy,
    VipDiscountStrategy,
)


def sample_items() -> list[dict[str, object]]:
    return [
        {"sku": "BOOK-001", "name": "Architecture Book", "quantity": 2, "unit_price": 120.0},
        {"sku": "MUG-001", "name": "Coffee Mug", "quantity": 1, "unit_price": 35.5},
    ]


def _default_discount_resolver() -> DefaultDiscountStrategyResolver:
    return DefaultDiscountStrategyResolver(
        registry={
            CustomerType.NORMAL: NoDiscountStrategy(),
            CustomerType.VIP: VipDiscountStrategy(),
            CustomerType.CORPORATE: CorporateDiscountStrategy(),
        },
        fallback=NoDiscountStrategy(),
    )


@pytest.fixture
def factory() -> PedidoFactory:
    return PedidoFactory.from_discount_resolver(_default_discount_resolver())


@pytest.mark.parametrize(
    ("customer_type", "expected_customer_type", "expected_discount", "expected_total"),
    [
        ("normal", CustomerType.NORMAL, 0.0, 275.5),
        ("vip", CustomerType.VIP, 27.55, 247.95),
        ("corporate", CustomerType.CORPORATE, 41.32, 234.18),
    ],
)
def test_pedido_factory_creates_supported_customer_orders(
    factory: PedidoFactory,
    customer_type: str,
    expected_customer_type: CustomerType,
    expected_discount: float,
    expected_total: float,
) -> None:
    order = factory.create_order("Ana", customer_type, sample_items())

    assert order.id is None
    assert order.customer_type == expected_customer_type
    assert order.subtotal == 275.5
    assert order.discount == expected_discount
    assert order.total == expected_total
    assert order.status == OrderStatus.CREATED
    assert len(order.items) == 2


@pytest.mark.parametrize(
    "order_factory",
    [
        NormalOrderFactory(_default_discount_resolver()),
        VipOrderFactory(_default_discount_resolver()),
        CorporateOrderFactory(_default_discount_resolver()),
    ],
)
def test_customer_factories_are_liskov_substitutable(
    order_factory: OrderFactoryInterface,
) -> None:
    order = order_factory.create("Ana", sample_items())

    assert order.status == OrderStatus.CREATED
    assert order.subtotal == 275.5
    assert order.total > 0.0


def test_pedido_factory_rejects_unsupported_customer_type(factory: PedidoFactory) -> None:
    with pytest.raises(ValueError):
        factory.create_order("Ana", "partner", sample_items())
