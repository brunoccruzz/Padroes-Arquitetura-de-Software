from src.interfaces import OrderRepositoryInterface


class ReportService:
    def __init__(self, repository: OrderRepositoryInterface):
        self.repository = repository

    def generate_report(self) -> str:
        total_orders, revenue, by_status, by_customer_type = self.repository.report_summary()
        status_text = ", ".join(f"{status}={count}" for status, count in by_status.items())
        customer_text = ", ".join(
            f"{customer_type}={count}" for customer_type, count in by_customer_type.items()
        )
        return (
            "Orders report\n"
            f"Total orders: {total_orders}\n"
            f"Gross revenue: {revenue:.2f}\n"
            f"By status: {status_text}\n"
            f"By customer type: {customer_text}"
        )
