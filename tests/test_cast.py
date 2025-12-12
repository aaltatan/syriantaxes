# ruff: noqa: S101, PLR0913

from decimal import Decimal

import pytest
from syriantaxes.cast import cast_to_decimal
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
def test_cast_to_decimal_with_number_valid_inputs(
    value: Number, expected: Decimal
) -> None:
    assert isinstance(cast_to_decimal(value), Decimal)
    assert cast_to_decimal(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        {"a": 100},
        [1, 2],
        (1, 3),
        {1, 2},
    ],
)
def test_cast_to_decimal_with_number_invalid_inputs(value: Number) -> None:
    with pytest.raises(TypeError):
        cast_to_decimal(value)


@pytest.mark.parametrize(
    "value, lt, gt, lte, gte, expected",
    [
        (-1, None, None, None, None, Decimal(-1)),
        (100, 0, None, None, None, Decimal("100.00")),
        (0, 0, None, None, None, Decimal(0)),
        (1, 0, 1, None, None, Decimal(1)),
        (0.1, None, None, 0, 1, Decimal("0.1")),
        (50.01, None, None, 50, 100, Decimal("50.01")),
        (50.01, 50, 100, 50, 100, Decimal("50.01")),
    ],
)
def test_cast_to_decimal_with_validators_valid_inputs(
    value: Number,
    lt: Number | None,
    gt: Number | None,
    lte: Number | None,
    gte: Number | None,
    expected: Decimal,
) -> None:
    assert cast_to_decimal(value, lt=lt, gt=gt, lte=lte, gte=gte) == expected


@pytest.mark.parametrize(
    "value, lt, gt, lte, gte",
    [
        (-1, 0, None, None, None),
        (0, None, None, 0, None),
        (100, None, None, 0, 100),
        (1.2, 0, 1, None, None),
        (1, 0, 1, 0, 1),
    ],
)
def test_cast_to_decimal_with_validators_invalid_inputs(
    value: Number,
    lt: Number | None,
    gt: Number | None,
    lte: Number | None,
    gte: Number | None,
) -> None:
    with pytest.raises(ValueError):
        cast_to_decimal(value, lt=lt, gt=gt, lte=lte, gte=gte)
