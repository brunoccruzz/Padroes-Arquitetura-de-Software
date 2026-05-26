from dataclasses import dataclass, field
from enum import StrEnum


class CustomerType(StrEnum):
    NORMAL = "NORMAL"
    VIP = "VIP"
    CORPORATE = "CORPORATE"


class OrderStatus(StrEnum):
    CREATED = "CREATED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"


class PaymentMethod(StrEnum):
    CARD = "CARD"
    PIX = "PIX"
    BOLETO = "BOLETO"
    CRYPTO = "CRYPTO"


@dataclass(frozen=True)
class OrderItem:
    sku: str
    name: str
    quantity: int
    unit_price: float
    line_total: float


@dataclass(frozen=True)
class PaymentRecord:
    method: PaymentMethod
    amount: float
    status: str
    reference: str
    paid_at: str


@dataclass(frozen=True)
class Order:
    id: int | None
    customer_name: str
    customer_type: CustomerType
    subtotal: float
    discount: float
    total: float
    status: OrderStatus
    created_at: str
    items: list[OrderItem] = field(default_factory=list)
    payments: list[PaymentRecord] = field(default_factory=list)
