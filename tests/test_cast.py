from collections.abc import Callable
from decimal import Decimal

import pytest

from syriantaxes.cast import to_decimal, to_non_negative, to_positive, to_rate
from syriantaxes.types import Number


@pytest.mark.parametrize(
    "value, expected",
    [
        (100, Decimal("100.00")),
        (-100, Decimal("-100.00")),
        (Decimal("100.00"), Decimal("100.00")),
        (Decimal("-100.00"), Decimal("-100.00")),
        ("100.00", Decimal("100.00")),
        ("-100.00", Decimal("-100.00")),
        (100.22, Decimal("100.22")),
        (-100.22, Decimal("-100.22")),
    ],
)
def test_to_decimal_with_valid_inputs(value: Number, expected: Decimal) -> None:
    assert isinstance(to_decimal(value), Decimal)
    assert to_decimal(value) == expected


@pytest.mark.parametrize("value", [{"a": 100}, [1, 2], (1, 3), {1, 2}, "abc"])
def test_to_decimal_with_invalid_inputs(value: Number) -> None:
    with pytest.raises(TypeError):
        to_decimal(value)


@pytest.mark.parametrize("value", [0, 1, "0.5", Decimal(1_000_000)])
def test_to_non_negative_accepts_zero_and_above(value: Number) -> None:
    assert to_non_negative(value) == to_decimal(value)


@pytest.mark.parametrize("value", [0.5, 1, Decimal(100)])
def test_to_positive_accepts_above_zero(value: Number) -> None:
    assert to_positive(value) == to_decimal(value)


@pytest.mark.parametrize("value", [0, "0.11", 1])
def test_to_rate_accepts_zero_to_one(value: Number) -> None:
    assert to_rate(value) == to_decimal(value)


@pytest.mark.parametrize(
    "convert, value",
    [
        (to_non_negative, -1),
        (to_positive, 0),
        (to_positive, -0.5),
        (to_rate, -0.01),
        (to_rate, 1.01),
    ],
)
def test_validators_reject_out_of_range_values(
    convert: Callable[[Number], Decimal], value: Number
) -> None:
    with pytest.raises(ValueError):
        convert(value)
