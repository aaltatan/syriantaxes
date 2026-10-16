from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from syriantaxes import Bracket
from syriantaxes.bracket import bracket_tax
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
    _min: tuple[Number, Decimal], _max: tuple[Number, Decimal], rate: tuple[Number, Decimal]
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

    assert bracket == Bracket(min_expected, max_expected, rate_expected)


@pytest.mark.parametrize(
    "_min, _max, rate",
    [
        (300, 200, 0.05),
        (-100, 200, 0.05),
        (100, 200, 1.01),
        (100, 200, -0.01),
        (100, 50, -0.01),
        (100, 100, 0.05),
    ],
)
def test_brackets_init_with_invalid_args(_min: Number, _max: Number, rate: Number) -> None:
    with pytest.raises(ValueError):
        Bracket(_min, _max, rate)


def test_brackets_are_immutable() -> None:
    bracket = Bracket(100, 200, 0.05)

    with pytest.raises(FrozenInstanceError):
        bracket.min = Decimal(150)  # type: ignore[misc]


@pytest.mark.parametrize(
    "salary, expected_tax",
    [
        (Decimal(50), Decimal(0)),
        (Decimal(100), Decimal(0)),
        (Decimal(150), Decimal("2.5")),
        (Decimal(200), Decimal(5)),
        (Decimal(1_000), Decimal(5)),
    ],
)
def test_bracket_tax_only_taxes_the_part_inside_the_bracket(
    salary: Decimal, expected_tax: Decimal
) -> None:
    assert bracket_tax(Bracket(100, 200, 0.05), salary) == expected_tax
