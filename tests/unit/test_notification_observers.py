import pytest
from src.interfaces import NotificationObserverInterface
from src.models import Order, CustomerType, OrderStatus
from src.observers import (
    EmailNotificationObserver,
    SmsNotificationObserver,
    ManagerNotificationObserver,
    WhatsAppNotificationObserver,
)


@pytest.fixture
def sample_order_normal() -> Order:
    return Order(
        id=1,
        customer_name="Ana",
        customer_type=CustomerType.NORMAL,
        subtotal=100.0,
        discount=0.0,
        total=100.0,
        status=OrderStatus.CREATED,
        created_at="2026-05-25T08:00:00",
        items=[],
        payments=[],
    )


@pytest.fixture
def sample_order_vip() -> Order:
    return Order(
        id=2,
        customer_name="Bruno",
        customer_type=CustomerType.VIP,
        subtotal=100.0,
        discount=10.0,
        total=90.0,
        status=OrderStatus.CREATED,
        created_at="2026-05-25T08:00:00",
        items=[],
        payments=[],
    )


@pytest.fixture
def sample_order_corporate() -> Order:
    return Order(
        id=3,
        customer_name="ACME",
        customer_type=CustomerType.CORPORATE,
        subtotal=100.0,
        discount=15.0,
        total=85.0,
        status=OrderStatus.CREATED,
        created_at="2026-05-25T08:00:00",
        items=[],
        payments=[],
    )


def test_whatsapp_observer_implements_interface() -> None:
    observer = WhatsAppNotificationObserver()
    assert isinstance(observer, NotificationObserverInterface)


def test_whatsapp_observer_update_runs_successfully(
    sample_order_normal: Order,
    sample_order_vip: Order,
    sample_order_corporate: Order,
) -> None:
    observer = WhatsAppNotificationObserver()
    # Call update on all profiles, should run without error
    observer.update(sample_order_normal)
    observer.update(sample_order_vip)
    observer.update(sample_order_corporate)


def test_email_observer_implements_interface() -> None:
    observer = EmailNotificationObserver()
    assert isinstance(observer, NotificationObserverInterface)


def test_email_observer_update_runs_successfully(
    sample_order_normal: Order,
    sample_order_vip: Order,
    sample_order_corporate: Order,
) -> None:
    observer = EmailNotificationObserver()
    observer.update(sample_order_normal)
    observer.update(sample_order_vip)
    observer.update(sample_order_corporate)


def test_sms_observer_implements_interface() -> None:
    observer = SmsNotificationObserver()
    assert isinstance(observer, NotificationObserverInterface)


def test_sms_observer_update_runs_successfully(
    sample_order_normal: Order,
    sample_order_vip: Order,
    sample_order_corporate: Order,
) -> None:
    observer = SmsNotificationObserver()
    observer.update(sample_order_normal)
    observer.update(sample_order_vip)
    observer.update(sample_order_corporate)


def test_manager_observer_implements_interface() -> None:
    observer = ManagerNotificationObserver()
    assert isinstance(observer, NotificationObserverInterface)


def test_manager_observer_update_runs_successfully(
    sample_order_normal: Order,
    sample_order_vip: Order,
    sample_order_corporate: Order,
) -> None:
    observer = ManagerNotificationObserver()
    observer.update(sample_order_normal)
    observer.update(sample_order_vip)
    observer.update(sample_order_corporate)
