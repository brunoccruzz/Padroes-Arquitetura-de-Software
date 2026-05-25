from src.interfaces import OrderRepositoryInterface
from src.models import OrderStatus, PaymentMethod
from src.strategies.payment_strategy import PaymentStrategyResolverInterface


class PaymentService:
    def __init__(
        self,
        repository: OrderRepositoryInterface,
        payment_resolver: PaymentStrategyResolverInterface,
    ) -> None:
        self.repository = repository
        self.payment_resolver = payment_resolver

    def pay_order(self, order_id: int, method: str) -> dict[str, object]:
        order = self.repository.get_by_id(order_id)
        if order is None:
            raise ValueError("order not found")
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("cancelled orders cannot be paid")

        payment_method = PaymentMethod(method.upper())
        payment = self.payment_resolver.resolve(payment_method).execute(order_id, order.total)
        self.repository.add_payment(order_id, payment)
        self.repository.update_status(order_id, OrderStatus.PAID)
        return {
            "order_id": order_id,
            "method": payment.method.value,
            "amount": payment.amount,
            "status": payment.status,
            "reference": payment.reference,
        }
