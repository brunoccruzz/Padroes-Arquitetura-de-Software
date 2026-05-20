import sqlite3

from src.interfaces import OrderRepositoryInterface
from src.models import CustomerType, Order, OrderItem, OrderStatus, PaymentMethod, PaymentRecord


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, db_name: str = "orders.db"):
        self.db_name = db_name
        self._create_tables()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def _create_tables(self) -> None:
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_type TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                reference TEXT NOT NULL,
                paid_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        connection.close()

    def save(self, order: Order) -> Order:
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO orders (
                customer_name, customer_type, subtotal, discount, total, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order.customer_name,
                order.customer_type.value,
                order.subtotal,
                order.discount,
                order.total,
                order.status.value,
                order.created_at,
            ),
        )
        order_id = cursor.lastrowid
        for item in order.items:
            cursor.execute(
                """
                INSERT INTO order_items (
                    order_id, sku, name, quantity, unit_price, line_total
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item.sku,
                    item.name,
                    item.quantity,
                    item.unit_price,
                    item.line_total,
                ),
            )
        connection.commit()
        connection.close()
        saved_order = self.get_by_id(int(order_id))
        if saved_order is None:
            raise RuntimeError("saved order could not be loaded")
        return saved_order

    def get_by_id(self, order_id: int) -> Order | None:
        connection = self._connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order is None:
            connection.close()
            return None

        cursor.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,))
        item_rows = cursor.fetchall()
        cursor.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY id", (order_id,))
        payment_rows = cursor.fetchall()
        connection.close()
        return Order(
            id=order["id"],
            customer_name=order["customer_name"],
            customer_type=CustomerType(order["customer_type"]),
            subtotal=order["subtotal"],
            discount=order["discount"],
            total=order["total"],
            status=OrderStatus(order["status"]),
            created_at=order["created_at"],
            items=[
                OrderItem(
                    sku=item["sku"],
                    name=item["name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    line_total=item["line_total"],
                )
                for item in item_rows
            ],
            payments=[
                PaymentRecord(
                    method=PaymentMethod(payment["method"]),
                    amount=payment["amount"],
                    status=payment["status"],
                    reference=payment["reference"],
                    paid_at=payment["paid_at"],
                )
                for payment in payment_rows
            ],
        )

    def add_payment(self, order_id: int, payment: PaymentRecord) -> None:
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO payments (order_id, method, amount, status, reference, paid_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                payment.method.value,
                payment.amount,
                payment.status,
                payment.reference,
                payment.paid_at,
            ),
        )
        connection.commit()
        connection.close()

    def update_status(self, order_id: int, status: OrderStatus) -> bool:
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status.value, order_id))
        connection.commit()
        changed = cursor.rowcount > 0
        connection.close()
        return changed

    def report_summary(self) -> tuple[int, float, dict[str, int], dict[str, int]]:
        connection = self._connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS total_orders, COALESCE(SUM(total), 0) AS revenue FROM orders"
        )
        summary = cursor.fetchone()
        cursor.execute(
            "SELECT status, COUNT(*) AS count FROM orders GROUP BY status ORDER BY status"
        )
        by_status = {row["status"]: row["count"] for row in cursor.fetchall()}
        cursor.execute(
            """
            SELECT customer_type, COUNT(*) AS count
            FROM orders
            GROUP BY customer_type
            ORDER BY customer_type
            """
        )
        by_customer_type = {row["customer_type"]: row["count"] for row in cursor.fetchall()}
        connection.close()
        return summary["total_orders"], summary["revenue"], by_status, by_customer_type
