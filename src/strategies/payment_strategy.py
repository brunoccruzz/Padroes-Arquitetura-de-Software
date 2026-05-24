from abc import ABC, abstractmethod
from datetime import datetime

from src.models import PaymentMethod, PaymentRecord


class PaymentStrategyInterface(ABC):
    @abstractmethod
    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        raise NotImplementedError


class PaymentStrategyResolverInterface(ABC):
    @abstractmethod
    def resolve(self, method: PaymentMethod) -> PaymentStrategyInterface:
        raise NotImplementedError


class CardPaymentStrategy(PaymentStrategyInterface):
    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        return PaymentRecord(
            method=PaymentMethod.CARD,
            amount=amount,
            status="APPROVED",
            reference=f"CARD-{order_id:06d}",
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


class PixPaymentStrategy(PaymentStrategyInterface):
    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        return PaymentRecord(
            method=PaymentMethod.PIX,
            amount=amount,
            status="APPROVED",
            reference=f"PIX-{order_id:06d}",
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


class BoletoPaymentStrategy(PaymentStrategyInterface):
    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        return PaymentRecord(
            method=PaymentMethod.BOLETO,
            amount=amount,
            status="APPROVED",
            reference=f"BOL-{order_id:06d}",
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


class DefaultPaymentStrategyResolver(PaymentStrategyResolverInterface):
    def __init__(self) -> None:
        self._registry: dict[PaymentMethod, PaymentStrategyInterface] = {
            PaymentMethod.CARD: CardPaymentStrategy(),
            PaymentMethod.PIX: PixPaymentStrategy(),
            PaymentMethod.BOLETO: BoletoPaymentStrategy(),
        }

    def resolve(self, method: PaymentMethod) -> PaymentStrategyInterface:
        strategy = self._registry.get(method)
        if strategy is None:
            raise ValueError(f"unsupported payment method: {method}")
        return strategy
