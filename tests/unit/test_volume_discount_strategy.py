import pytest

from src.strategies.discount_strategy import DiscountStrategyInterface
from src.strategies.volume_discount_strategy import VolumeDiscountStrategy


@pytest.fixture
def strategy() -> VolumeDiscountStrategy:
    return VolumeDiscountStrategy()


def test_implements_discount_strategy_interface(strategy: VolumeDiscountStrategy) -> None:
    assert isinstance(strategy, DiscountStrategyInterface)


def test_no_discount_below_200(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(199.99) == 0.0


def test_no_discount_at_zero(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(0.0) == 0.0


def test_5_percent_at_200(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(200.0) == 10.0


def test_5_percent_just_below_500(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(499.99) == 25.0


def test_10_percent_at_500(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(500.0) == 50.0


def test_10_percent_just_below_1000(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(999.99) == 100.0


def test_15_percent_at_1000(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(1000.0) == 150.0


def test_15_percent_above_1000(strategy: VolumeDiscountStrategy) -> None:
    assert strategy.calculate(2000.0) == 300.0


@pytest.mark.parametrize(
    ("subtotal", "expected_discount"),
    [
        (0.0, 0.0),
        (100.0, 0.0),
        (199.99, 0.0),
        (200.0, 10.0),
        (300.0, 15.0),
        (499.99, 25.0),
        (500.0, 50.0),
        (750.0, 75.0),
        (999.99, 100.0),
        (1000.0, 150.0),
        (1500.0, 225.0),
    ],
)
def test_tiers_parametrized(
    strategy: VolumeDiscountStrategy, subtotal: float, expected_discount: float
) -> None:
    assert strategy.calculate(subtotal) == expected_discount
