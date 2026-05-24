from abc import ABC, abstractmethod

from src.models import CustomerType


class DiscountStrategyInterface(ABC):
    @abstractmethod
    def calculate(self, subtotal: float) -> float:
        raise NotImplementedError


class DiscountStrategyResolverInterface(ABC):
    @abstractmethod
    def resolve(self, customer_type: CustomerType) -> DiscountStrategyInterface:
        raise NotImplementedError


class NoDiscountStrategy(DiscountStrategyInterface):
    def calculate(self, subtotal: float) -> float:
        return 0.0


class VipDiscountStrategy(DiscountStrategyInterface):
    _RATE: float = 0.10

    def calculate(self, subtotal: float) -> float:
        return round(subtotal * self._RATE, 2)


class CorporateDiscountStrategy(DiscountStrategyInterface):
    _RATE: float = 0.15

    def calculate(self, subtotal: float) -> float:
        return round(subtotal * self._RATE, 2)


class DefaultDiscountStrategyResolver(DiscountStrategyResolverInterface):
    def __init__(self) -> None:
        self._registry: dict[CustomerType, DiscountStrategyInterface] = {
            CustomerType.NORMAL: NoDiscountStrategy(),
            CustomerType.VIP: VipDiscountStrategy(),
            CustomerType.CORPORATE: CorporateDiscountStrategy(),
        }

    def resolve(self, customer_type: CustomerType) -> DiscountStrategyInterface:
        return self._registry.get(customer_type, NoDiscountStrategy())
