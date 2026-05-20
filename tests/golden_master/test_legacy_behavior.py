import pytest

from legacy_system import LegacyOrderSystem


def make_system(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return LegacyOrderSystem()


def sample_items():
    return [
        {"sku": "BOOK-001", "name": "Architecture Book", "quantity": 2, "unit_price": 120.0},
        {"sku": "MUG-001", "name": "Coffee Mug", "quantity": 1, "unit_price": 35.5},
    ]


def comparable_order(order):
    return {
        "customer_name": order["customer_name"],
        "customer_type": order["customer_type"],
        "subtotal": order["subtotal"],
        "discount": order["discount"],
        "total": order["total"],
        "status": order["status"],
        "items": order["items"],
        "payments": [
            {
                "method": payment["method"],
                "amount": payment["amount"],
                "status": payment["status"],
                "reference": payment["reference"],
            }
            for payment in order["payments"]
        ],
    }


def test_create_normal_order(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)

    order = system.create_order("Ana", "normal", sample_items())

    assert comparable_order(order) == {
        "customer_name": "Ana",
        "customer_type": "NORMAL",
        "subtotal": 275.5,
        "discount": 0.0,
        "total": 275.5,
        "status": "CREATED",
        "items": [
            {
                "sku": "BOOK-001",
                "name": "Architecture Book",
                "quantity": 2,
                "unit_price": 120.0,
                "line_total": 240.0,
            },
            {
                "sku": "MUG-001",
                "name": "Coffee Mug",
                "quantity": 1,
                "unit_price": 35.5,
                "line_total": 35.5,
            },
        ],
        "payments": [],
    }


def test_create_vip_order(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)

    order = system.create_order("Bruno", "vip", sample_items())

    assert comparable_order(order)["customer_type"] == "VIP"
    assert comparable_order(order)["subtotal"] == 275.5
    assert comparable_order(order)["discount"] == 27.55
    assert comparable_order(order)["total"] == 247.95
    assert comparable_order(order)["status"] == "CREATED"


def test_create_corporate_order(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)

    order = system.create_order("ACME", "corporate", sample_items())

    assert comparable_order(order)["customer_type"] == "CORPORATE"
    assert comparable_order(order)["subtotal"] == 275.5
    assert comparable_order(order)["discount"] == 41.32
    assert comparable_order(order)["total"] == 234.18
    assert comparable_order(order)["status"] == "CREATED"


@pytest.mark.parametrize(
    ("method", "reference"),
    [
        ("card", "CARD-000001"),
        ("pix", "PIX-000001"),
        ("boleto", "BOL-000001"),
    ],
)
def test_payment_methods(tmp_path, monkeypatch, method, reference):
    system = make_system(tmp_path, monkeypatch)
    order = system.create_order("Ana", "normal", sample_items())

    payment = system.pay_order(order["id"], method)
    paid_order = system.get_order(order["id"])

    assert payment == {
        "order_id": 1,
        "method": method.upper(),
        "amount": 275.5,
        "status": "APPROVED",
        "reference": reference,
    }
    assert comparable_order(paid_order)["status"] == "PAID"
    assert comparable_order(paid_order)["payments"] == [
        {
            "method": method.upper(),
            "amount": 275.5,
            "status": "APPROVED",
            "reference": reference,
        }
    ]


def test_update_status(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)
    order = system.create_order("Ana", "normal", sample_items())

    updated = system.update_status(order["id"], "shipped")

    assert comparable_order(updated)["status"] == "SHIPPED"


def test_cancel_order(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)
    order = system.create_order("Ana", "normal", sample_items())

    cancelled = system.cancel_order(order["id"])

    assert comparable_order(cancelled)["status"] == "CANCELLED"


def test_report_generation(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)
    first = system.create_order("Ana", "normal", sample_items())
    system.create_order("Bruno", "vip", sample_items())
    third = system.create_order("ACME", "corporate", sample_items())
    system.pay_order(first["id"], "pix")
    system.cancel_order(third["id"])

    report = system.generate_report()

    assert report == (
        "Orders report\n"
        "Total orders: 3\n"
        "Gross revenue: 757.63\n"
        "By status: CANCELLED=1, CREATED=1, PAID=1\n"
        "By customer type: CORPORATE=1, NORMAL=1, VIP=1"
    )


def test_paid_order_cannot_be_cancelled(tmp_path, monkeypatch):
    system = make_system(tmp_path, monkeypatch)
    order = system.create_order("Ana", "normal", sample_items())
    system.pay_order(order["id"], "card")

    with pytest.raises(ValueError, match="paid orders cannot be cancelled"):
        system.cancel_order(order["id"])
