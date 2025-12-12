# ruff: noqa: S101

from decimal import Decimal

import pytest
from syriantaxes import Bracket
from syriantaxes.types import Number


@pytest.mark.parametrize(
    "_min, _max, rate",
    [
        (
            (Decimal("100.00"), Decimal("100.00")),
            (Decimal("200.00"), Decimal("200.00")),
            (Decimal("0.05"), Decimal("0.05")),
        ),
        (
            (100, Decimal("100.00")),
            (200, Decimal("200.00")),
            (0.05, Decimal("0.05")),
        ),
        (
            ("100.00", Decimal("100.00")),
            ("200.00", Decimal("200.00")),
            ("0.05", Decimal("0.05")),
        ),
        (
            (100.00, Decimal("100.00")),
            (200.00, Decimal("200.00")),
            (0.05, Decimal("0.05")),
        ),
    ],
)
def test_brackets_init_with_valid_args(
    _min: tuple[Number, Decimal],
    _max: tuple[Number, Decimal],
    rate: tuple[Number, Decimal],
) -> None:
    min_value, min_expected = _min
    max_value, max_expected = _max
    rate_value, rate_expected = rate

    bracket = Bracket(min_value, max_value, rate_value)

    assert isinstance(bracket.min, Decimal) is True
    assert isinstance(bracket.max, Decimal) is True
    assert isinstance(bracket.rate, Decimal) is True

    assert bracket.min == min_expected
    assert bracket.max == max_expected
    assert bracket.rate == rate_expected

    assert (str(bracket)) == (
        f"Bracket(min={min_value}, max={max_value}, rate={rate_value})"
    )


@pytest.mark.parametrize(
    "_min, _max, rate",
    [
        (300, 200, 0.05),
        (-100, 200, 0.05),
        (100, 200, 1.01),
        (100, 200, -0.01),
        (100, 50, -0.01),
    ],
)
def test_brackets_init_with_invalid_args(
    _min: Number, _max: Number, rate: Number
) -> None:
    with pytest.raises(ValueError):
        Bracket(_min, _max, rate)


@pytest.mark.parametrize(
    "_min, _max, rate",
    [
        (
            (100, Decimal("100.00"), -100),
            (200, Decimal("200.00"), 50),
            (0.05, Decimal("0.05"), 100),
        ),
    ],
)
def test_brackets_setters_with_valid_args(
    _min: tuple[Number, Decimal, Number],
    _max: tuple[Number, Decimal, Number],
    rate: tuple[Number, Decimal, Number],
):
    min_value, min_expected, min_invalid = _min
    max_value, max_expected, max_invalid = _max
    rate_value, rate_expected, rate_invalid = rate

    bracket = Bracket(min_value, max_value, rate_value)

    assert bracket.min == min_expected
    assert bracket.max == max_expected
    assert bracket.rate == rate_expected

    with pytest.raises(ValueError):
        bracket.min = min_invalid

    with pytest.raises(ValueError):
        bracket.max = max_invalid

    with pytest.raises(ValueError):
        bracket.rate = rate_invalid
