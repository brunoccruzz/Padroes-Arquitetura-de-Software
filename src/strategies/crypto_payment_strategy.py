"""
Estratégia de pagamento em criptomoeda para a Loja Verde.

Existe para permitir que clientes paguem com criptomoedas sem alterar nenhum
arquivo já versionado — demonstração empírica do Open-Closed Principle: o
sistema está fechado para modificação e aberto para extensão. Para disponibilizar
o método basta criar esta classe e injetá-la via ``PaymentStrategyResolverInterface``
ou diretamente em qualquer ponto que aceite ``PaymentStrategyInterface``.

Regra de negócio: sobre o valor base do pedido (``order.total``) incide uma taxa
operacional de 2%, de modo que o cliente paga ``amount * 1.02``. O acréscimo
cobre o custo de conversão e liquidação das criptomoedas.
"""

from datetime import datetime
from typing import cast

from src.models import PaymentMethod, PaymentRecord
from src.strategies.payment_strategy import PaymentStrategyInterface


class CryptoPaymentStrategy(PaymentStrategyInterface):
    """Processa pagamentos em criptomoeda com taxa operacional de 2% sobre o pedido."""

    _FEE_RATE: float = 0.02

    def execute(self, order_id: int, amount: float) -> PaymentRecord:
        """Aplica taxa de 2% e retorna o registro de pagamento aprovado."""
        amount_with_fee = round(amount * (1.0 + self._FEE_RATE), 2)
        return PaymentRecord(
            method=cast(PaymentMethod, "CRYPTO"),
            amount=amount_with_fee,
            status="APPROVED",
            reference=f"CRYPTO-{order_id:06d}",
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
