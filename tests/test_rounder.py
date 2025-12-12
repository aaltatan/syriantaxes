# ruff: noqa: S101

from decimal import Decimal

import pytest
from syriantaxes import Rounder, RoundingMethod
from syriantaxes.types import Number


@pytest.mark.parametrize(
    "method, to_nearest, amount, expected",
    [
        (RoundingMethod.CEILING, 100, 150_150, Decimal(150_200)),
        (RoundingMethod.FLOOR, 100, 150_150, Decimal(150_100)),
        (RoundingMethod.CEILING, 10, 150_155, Decimal(150_160)),
        (RoundingMethod.FLOOR, 10, 150_155, Decimal(150_150)),
        (RoundingMethod.CEILING, 1, 150_155.5, Decimal(150_156)),
        (RoundingMethod.FLOOR, 1, 150_155.3, Decimal(150_155)),
        (RoundingMethod.CEILING, 0.5, 150_155.3, Decimal("150_155.5")),
        (RoundingMethod.CEILING, 0.3, 150_155.3, Decimal("150_155.4")),
        (RoundingMethod.FLOOR, 0.3, 150_155.3, Decimal("150_155.1")),
    ],
)
def test_rounder_init_with_valid_args(
    method: RoundingMethod,
    to_nearest: Number,
    amount: Number,
    expected: Decimal,
) -> None:
    rounder = Rounder(method, to_nearest)
    result = rounder.round(amount)

    assert isinstance(rounder.to_nearest, Decimal)
    assert isinstance(result, Decimal)

    assert result == expected


def test_rounder_init_with_invalid_args() -> None:
    with pytest.raises(ValueError):
        Rounder(RoundingMethod.CEILING, -100)


def test_rounder_init_with_invalid_setter() -> None:
    rounder = Rounder(RoundingMethod.CEILING, 100)

    with pytest.raises(ValueError):
        rounder.to_nearest = -100
