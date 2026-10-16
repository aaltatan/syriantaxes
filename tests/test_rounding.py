from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

import pytest

from syriantaxes import round_to, to_cents


@pytest.mark.parametrize(
    "step, method, amount, expected",
    [
        (Decimal(100), ROUND_CEILING, Decimal(150_150), Decimal(150_200)),
        (Decimal(100), ROUND_FLOOR, Decimal(150_150), Decimal(150_100)),
        (Decimal(10), ROUND_CEILING, Decimal(150_155), Decimal(150_160)),
        (Decimal(10), ROUND_FLOOR, Decimal(150_155), Decimal(150_150)),
        (Decimal(1), ROUND_CEILING, Decimal("150155.5"), Decimal(150_156)),
        (Decimal(1), ROUND_FLOOR, Decimal("150155.3"), Decimal(150_155)),
        (Decimal("0.5"), ROUND_CEILING, Decimal("150155.3"), Decimal("150155.5")),
        (Decimal("0.3"), ROUND_CEILING, Decimal("150155.3"), Decimal("150155.4")),
        (Decimal("0.3"), ROUND_FLOOR, Decimal("150155.3"), Decimal("150155.1")),
    ],
)
def test_round_to(step: Decimal, method: str, amount: Decimal, expected: Decimal) -> None:
    assert round_to(step, method)(amount) == expected


def test_to_cents_rounds_half_even() -> None:
    assert to_cents(Decimal("0.125")) == Decimal("0.12")
    assert to_cents(Decimal("0.135")) == Decimal("0.14")


@pytest.mark.parametrize("step", [Decimal(0), Decimal(-100)])
def test_round_to_rejects_a_non_positive_step(step: Decimal) -> None:
    with pytest.raises(ValueError, match="step"):
        round_to(step)
