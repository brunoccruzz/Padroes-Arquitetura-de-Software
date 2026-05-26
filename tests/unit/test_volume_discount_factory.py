import pytest

from src.factories.order_factory import PedidoFactory
from src.factories.volume_discount_factory import VolumeDiscountPedidoFactory
from src.models import CustomerType
from src.strategies.discount_strategy import DefaultDiscountStrategyResolver, NoDiscountStrategy


@pytest.fixture
def factory() -> VolumeDiscountPedidoFactory:
    resolver = DefaultDiscountStrategyResolver(
        registry={CustomerType.NORMAL: NoDiscountStrategy()},
        fallback=NoDiscountStrategy(),
    )
    return VolumeDiscountPedidoFactory(PedidoFactory.from_discount_resolver(resolver))


def test_no_volume_discount_below_threshold(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 2, "unit_price": 100.0}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.total == pytest.approx(200.0)
    assert order.items[0].unit_price == pytest.approx(100.0)


def test_no_volume_discount_at_exactly_2_units(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 2, "unit_price": 100.0}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.items[0].unit_price == pytest.approx(100.0)


def test_15_percent_discount_at_threshold_of_3(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 3, "unit_price": 100.0}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.items[0].unit_price == pytest.approx(85.0)
    assert order.total == pytest.approx(255.0)


def test_15_percent_discount_above_threshold(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 5, "unit_price": 200.0}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.items[0].unit_price == pytest.approx(170.0)
    assert order.total == pytest.approx(850.0)


def test_discount_applies_only_to_qualifying_items(factory: VolumeDiscountPedidoFactory) -> None:
    items = [
        {"sku": "A", "name": "Widget", "quantity": 3, "unit_price": 100.0},
        {"sku": "B", "name": "Gadget", "quantity": 1, "unit_price": 50.0},
    ]
    order = factory.create_order("Test", "NORMAL", items)
    widget = next(i for i in order.items if i.sku == "A")
    gadget = next(i for i in order.items if i.sku == "B")
    assert widget.unit_price == pytest.approx(85.0)
    assert gadget.unit_price == pytest.approx(50.0)
    assert order.total == pytest.approx(305.0)


def test_volume_discount_stacks_with_customer_type_discount() -> None:
    from src.models import CustomerType
    from src.strategies.discount_strategy import (
        DefaultDiscountStrategyResolver,
        NoDiscountStrategy,
        VipDiscountStrategy,
    )

    resolver = DefaultDiscountStrategyResolver(
        registry={
            CustomerType.NORMAL: NoDiscountStrategy(),
            CustomerType.VIP: VipDiscountStrategy(),
        },
        fallback=NoDiscountStrategy(),
    )
    factory = VolumeDiscountPedidoFactory(PedidoFactory.from_discount_resolver(resolver))
    items = [{"sku": "A", "name": "Widget", "quantity": 3, "unit_price": 100.0}]
    order = factory.create_order("Test", "VIP", items)
    # subtotal = 3 * 85.0 = 255.0; VIP discount = 10% = 25.5; total = 229.5
    assert order.subtotal == pytest.approx(255.0)
    assert order.discount == pytest.approx(25.5)
    assert order.total == pytest.approx(229.5)


def test_implements_pedido_factory_interface() -> None:
    from src.factories.order_factory import PedidoFactoryInterface

    resolver = DefaultDiscountStrategyResolver(
        registry={},
        fallback=NoDiscountStrategy(),
    )
    f = VolumeDiscountPedidoFactory(PedidoFactory.from_discount_resolver(resolver))
    assert isinstance(f, PedidoFactoryInterface)


def test_quantity_as_string_is_accepted(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": "3", "unit_price": 100.0}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.items[0].unit_price == pytest.approx(85.0)


def test_unit_price_as_string_is_accepted(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 3, "unit_price": "100.0"}]
    order = factory.create_order("Test", "NORMAL", items)
    assert order.items[0].unit_price == pytest.approx(85.0)


def test_invalid_quantity_type_raises_type_error(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": None, "unit_price": 100.0}]
    with pytest.raises(TypeError, match="quantity must be numeric"):
        factory.create_order("Test", "NORMAL", items)


def test_invalid_unit_price_type_raises_type_error(factory: VolumeDiscountPedidoFactory) -> None:
    items = [{"sku": "A", "name": "Widget", "quantity": 3, "unit_price": None}]
    with pytest.raises(TypeError, match="unit_price must be numeric"):
        factory.create_order("Test", "NORMAL", items)
