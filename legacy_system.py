import sqlite3
from datetime import datetime


DB_NAME = "orders.db"


class LegacyOrderSystem:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
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

    def create_order(self, customer_name, customer_type, items):
        if not items:
            raise ValueError("order must have at least one item")

        normalized_type = customer_type.upper()
        subtotal = 0.0
        prepared_items = []
        for item in items:
            quantity = int(item["quantity"])
            unit_price = float(item["unit_price"])
            line_total = round(quantity * unit_price, 2)
            subtotal += line_total
            prepared_items.append(
                {
                    "sku": item["sku"],
                    "name": item["name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                }
            )

        discount_rate = 0.0
        if normalized_type == "VIP":
            discount_rate = 0.10
        elif normalized_type == "CORPORATE":
            discount_rate = 0.15

        subtotal = round(subtotal, 2)
        discount = round(subtotal * discount_rate, 2)
        total = round(subtotal - discount, 2)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO orders (
                customer_name, customer_type, subtotal, discount, total, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (customer_name, normalized_type, subtotal, discount, total, "CREATED", now),
        )
        order_id = cursor.lastrowid
        for item in prepared_items:
            cursor.execute(
                """
                INSERT INTO order_items (
                    order_id, sku, name, quantity, unit_price, line_total
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["sku"],
                    item["name"],
                    item["quantity"],
                    item["unit_price"],
                    item["line_total"],
                ),
            )
        connection.commit()
        connection.close()
        return self.get_order(order_id)

    def get_order(self, order_id):
        connection = self._connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order is None:
            connection.close()
            return None

        cursor.execute("SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,))
        items = cursor.fetchall()
        cursor.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY id", (order_id,))
        payments = cursor.fetchall()
        connection.close()
        return {
            "id": order["id"],
            "customer_name": order["customer_name"],
            "customer_type": order["customer_type"],
            "subtotal": order["subtotal"],
            "discount": order["discount"],
            "total": order["total"],
            "status": order["status"],
            "created_at": order["created_at"],
            "items": [
                {
                    "sku": item["sku"],
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "line_total": item["line_total"],
                }
                for item in items
            ],
            "payments": [
                {
                    "method": payment["method"],
                    "amount": payment["amount"],
                    "status": payment["status"],
                    "reference": payment["reference"],
                    "paid_at": payment["paid_at"],
                }
                for payment in payments
            ],
        }

    def pay_order(self, order_id, method):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("order not found")
        if order["status"] == "CANCELLED":
            raise ValueError("cancelled orders cannot be paid")

        normalized_method = method.upper()
        if normalized_method not in ("CARD", "PIX", "BOLETO"):
            raise ValueError("unsupported payment method")

        reference_prefix = {"CARD": "CARD", "PIX": "PIX", "BOLETO": "BOL"}[normalized_method]
        reference = f"{reference_prefix}-{order_id:06d}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO payments (order_id, method, amount, status, reference, paid_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, normalized_method, order["total"], "APPROVED", reference, now),
        )
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", ("PAID", order_id))
        connection.commit()
        connection.close()
        return {
            "order_id": order_id,
            "method": normalized_method,
            "amount": order["total"],
            "status": "APPROVED",
            "reference": reference,
        }

    def update_status(self, order_id, status):
        normalized_status = status.upper()
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (normalized_status, order_id))
        connection.commit()
        changed = cursor.rowcount
        connection.close()
        if changed == 0:
            raise ValueError("order not found")
        return self.get_order(order_id)

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("order not found")
        if order["status"] == "PAID":
            raise ValueError("paid orders cannot be cancelled")
        return self.update_status(order_id, "CANCELLED")

    def generate_report(self):
        connection = self._connect()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) AS total_orders, COALESCE(SUM(total), 0) AS revenue FROM orders")
        summary = cursor.fetchone()
        cursor.execute("SELECT status, COUNT(*) AS count FROM orders GROUP BY status ORDER BY status")
        by_status = cursor.fetchall()
        cursor.execute(
            "SELECT customer_type, COUNT(*) AS count FROM orders GROUP BY customer_type ORDER BY customer_type"
        )
        by_customer_type = cursor.fetchall()
        connection.close()

        status_text = ", ".join(f"{row['status']}={row['count']}" for row in by_status)
        customer_text = ", ".join(f"{row['customer_type']}={row['count']}" for row in by_customer_type)
        return (
            "Orders report\n"
            f"Total orders: {summary['total_orders']}\n"
            f"Gross revenue: {summary['revenue']:.2f}\n"
            f"By status: {status_text}\n"
            f"By customer type: {customer_text}"
        )
