from src.strategies.discount_strategy import DiscountStrategyInterface


class VolumeDiscountStrategy(DiscountStrategyInterface):
    """Progressive discount by subtotal tiers: 5% ≥200, 10% ≥500, 15% ≥1000."""

    _TIERS: tuple[tuple[float, float], ...] = (
        (1000.0, 0.15),
        (500.0, 0.10),
        (200.0, 0.05),
    )

    def calculate(self, subtotal: float) -> float:
        for threshold, rate in self._TIERS:
            if subtotal >= threshold:
                return round(subtotal * rate, 2)
        return 0.0
