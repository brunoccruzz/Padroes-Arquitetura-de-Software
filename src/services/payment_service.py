from datetime import datetime

from src.interfaces import OrderRepositoryInterface, PaymentReferenceProviderInterface
from src.models import OrderStatus, PaymentMethod, PaymentRecord


class SequentialPaymentReferenceProvider(PaymentReferenceProviderInterface):
    def reference_for(self, method: PaymentMethod, order_id: int) -> str:
        prefix = {
            PaymentMethod.CARD: "CARD",
            PaymentMethod.PIX: "PIX",
            PaymentMethod.BOLETO: "BOL",
        }[method]
        return f"{prefix}-{order_id:06d}"


class PaymentService:
    def __init__(
        self,
        repository: OrderRepositoryInterface,
        reference_provider: PaymentReferenceProviderInterface | None = None,
    ):
        self.repository = repository
        self.reference_provider = reference_provider or SequentialPaymentReferenceProvider()

    def pay_order(self, order_id: int, method: str) -> dict:
        order = self.repository.get_by_id(order_id)
        if order is None:
            raise ValueError("order not found")
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("cancelled orders cannot be paid")

        payment_method = PaymentMethod(method.upper())
        payment = PaymentRecord(
            method=payment_method,
            amount=order.total,
            status="APPROVED",
            reference=self.reference_provider.reference_for(payment_method, order_id),
            paid_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.repository.add_payment(order_id, payment)
        self.repository.update_status(order_id, OrderStatus.PAID)
        return {
            "order_id": order_id,
            "method": payment.method.value,
            "amount": payment.amount,
            "status": payment.status,
            "reference": payment.reference,
        }
