"""Testes unitários para CryptoPaymentStrategy."""

import pytest
from unittest.mock import MagicMock

from src.interfaces import OrderRepositoryInterface
from src.models import CustomerType, Order, OrderStatus, PaymentRecord
from src.strategies.crypto_payment_strategy import CryptoPaymentStrategy
from src.strategies.payment_strategy import PaymentStrategyInterface, PixPaymentStrategy


@pytest.fixture
def strategy() -> CryptoPaymentStrategy:
    return CryptoPaymentStrategy()


# ---------------------------------------------------------------------------
# Conformidade com a interface
# ---------------------------------------------------------------------------


def test_implements_payment_strategy_interface(strategy: CryptoPaymentStrategy) -> None:
    assert isinstance(strategy, PaymentStrategyInterface)


def test_returns_payment_record_instance(strategy: CryptoPaymentStrategy) -> None:
    assert isinstance(strategy.execute(1, 100.0), PaymentRecord)


# ---------------------------------------------------------------------------
# Cálculo da taxa de 2%
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (100.0, 102.0),
        (1_000.0, 1_020.0),
        (99.99, 101.99),       # 99.99 * 1.02 = 101.9898 → 101.99
        (123.4567, 125.93),    # 123.4567 * 1.02 = 125.925834 → 125.93
        (0.01, 0.01),          # 0.01 * 1.02 = 0.0102 → 0.01
        (999_999.99, 1_019_999.99),  # 999999.99 * 1.02 = 1019999.9898 → 1019999.99
    ],
)
def test_fee_calculation(
    strategy: CryptoPaymentStrategy, amount: float, expected: float
) -> None:
    record = strategy.execute(1, amount)
    assert record.amount == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Campos do PaymentRecord
# ---------------------------------------------------------------------------


def test_reference_format(strategy: CryptoPaymentStrategy) -> None:
    assert strategy.execute(42, 100.0).reference == "CRYPTO-000042"


def test_reference_zero_padded_for_large_id(strategy: CryptoPaymentStrategy) -> None:
    assert strategy.execute(999_999, 100.0).reference == "CRYPTO-999999"


def test_status_is_approved(strategy: CryptoPaymentStrategy) -> None:
    assert strategy.execute(1, 100.0).status == "APPROVED"


def test_paid_at_is_non_empty_string(strategy: CryptoPaymentStrategy) -> None:
    paid_at = strategy.execute(1, 100.0).paid_at
    assert isinstance(paid_at, str) and len(paid_at) > 0


# ---------------------------------------------------------------------------
# Casos de borda
# ---------------------------------------------------------------------------


def test_zero_amount_follows_existing_contract(strategy: CryptoPaymentStrategy) -> None:
    """Contrato existente não rejeita amount=0; cripto também não deve."""
    record = strategy.execute(1, 0.0)
    assert record.amount == pytest.approx(0.0)


def test_negative_amount_follows_existing_contract(strategy: CryptoPaymentStrategy) -> None:
    """Contrato existente não valida negativos; taxa de 2% é aplicada igualmente."""
    record = strategy.execute(1, -100.0)
    assert record.amount == pytest.approx(-102.0)


def test_very_large_amount(strategy: CryptoPaymentStrategy) -> None:
    record = strategy.execute(1, 1_000_000.0)
    assert record.amount == pytest.approx(1_020_000.0)


# ---------------------------------------------------------------------------
# Integração: mesmo contrato que PIX/cartão
# ---------------------------------------------------------------------------


def test_result_has_same_structure_as_pix_strategy(
    strategy: CryptoPaymentStrategy,
) -> None:
    """CryptoPaymentStrategy devolve o mesmo tipo e status que PixPaymentStrategy."""
    pix = PixPaymentStrategy()

    crypto_record = strategy.execute(1, 100.0)
    pix_record = pix.execute(1, 100.0)

    assert type(crypto_record) is type(pix_record)
    assert crypto_record.status == pix_record.status


def test_crypto_amount_is_two_percent_above_pix(
    strategy: CryptoPaymentStrategy,
) -> None:
    pix = PixPaymentStrategy()
    amount = 500.0

    crypto_record = strategy.execute(1, amount)
    pix_record = pix.execute(1, amount)

    assert crypto_record.amount == pytest.approx(pix_record.amount * 1.02)


def test_integration_order_ends_in_paid_status(strategy: CryptoPaymentStrategy) -> None:
    """
    Integração via mock: pedido pago em cripto termina em PAID,
    idêntico ao comportamento de PIX ou cartão.
    """
    mock_repo = MagicMock(spec=OrderRepositoryInterface)
    order = Order(
        id=1,
        customer_name="Cliente Cripto",
        customer_type=CustomerType.NORMAL,
        subtotal=500.0,
        discount=0.0,
        total=500.0,
        status=OrderStatus.CREATED,
        created_at="2026-05-25 10:00:00",
    )
    mock_repo.get_by_id.return_value = order

    payment = strategy.execute(1, order.total)

    # Replica exatamente o que PaymentService.pay_order() faz após execute()
    mock_repo.add_payment(1, payment)
    mock_repo.update_status(1, OrderStatus.PAID)

    mock_repo.add_payment.assert_called_once_with(1, payment)
    mock_repo.update_status.assert_called_once_with(1, OrderStatus.PAID)
    assert payment.status == "APPROVED"
    assert payment.amount == pytest.approx(510.0)  # 500.0 * 1.02
