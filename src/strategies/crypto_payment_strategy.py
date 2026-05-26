from datetime import datetime

from src.models import PaymentMethod, PaymentRecord
from src.strategies.payment_strategy import PaymentStrategyInterface


class CryptoPaymentStrategy(PaymentStrategyInterface):
    """Processa pagamentos em criptomoeda com taxa operacional de 2% sobre o pedido."""

    _FEE_RATE: float = 0.02

    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        amount_with_fee = round(amount * (1.0 + self._FEE_RATE), 2)
        return PaymentRecord(
            method=PaymentMethod.CRYPTO,
            amount=amount_with_fee,
            status="APPROVED",
            reference=f"CRYPTO-{order_id:06d}",
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
