from src.models import Order
from src.repositories import OrderRepository
from src.services import OrderService, PaymentService, ReportService


DB_NAME = "orders.db"


class LegacyOrderSystem:
    def __init__(self, db_name=DB_NAME):
        repository = OrderRepository(db_name)
        self.order_service = OrderService(repository)
        self.payment_service = PaymentService(repository)
        self.report_service = ReportService(repository)

    def create_order(self, customer_name, customer_type, items):
        order = self.order_service.create_order(customer_name, customer_type, items)
        return self._to_dict(order)

    def get_order(self, order_id):
        order = self.order_service.get_order(order_id)
        if order is None:
            return None
        return self._to_dict(order)

    def pay_order(self, order_id, method):
        return self.payment_service.pay_order(order_id, method)

    def update_status(self, order_id, status):
        order = self.order_service.update_status(order_id, status)
        return self._to_dict(order)

    def cancel_order(self, order_id):
        order = self.order_service.cancel_order(order_id)
        return self._to_dict(order)

    def generate_report(self):
        return self.report_service.generate_report()

    def _to_dict(self, order: Order) -> dict:
        return {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_type": order.customer_type.value,
            "subtotal": order.subtotal,
            "discount": order.discount,
            "total": order.total,
            "status": order.status.value,
            "created_at": order.created_at,
            "items": [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in order.items
            ],
            "payments": [
                {
                    "method": payment.method.value,
                    "amount": payment.amount,
                    "status": payment.status,
                    "reference": payment.reference,
                    "paid_at": payment.paid_at,
                }
                for payment in order.payments
            ],
        }
