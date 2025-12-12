# ruff: noqa: S101

from decimal import Decimal

import pytest
from syriantaxes import (
    Rounder,
    calculate_brackets_tax,
    calculate_fixed_tax,
    calculate_gross_compensation,
    calculate_gross_components,
    calculate_gross_salary,
)
from syriantaxes.types import Number


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (1_000_000, Decimal(50_000)),
        (2_000_000, Decimal(100_000)),
        (155_770, Decimal(7_800)),
        (221_300, Decimal(11_100)),
    ],
)
def test_calculate_fixed_tax(
    tax_rounder: Rounder,
    compensations_tax_rate: Decimal,
    amount: Number,
    expected_tax: Decimal,
) -> None:
    result = calculate_fixed_tax(amount, compensations_tax_rate, tax_rounder)

    assert isinstance(result, Decimal)
    assert result == expected_tax


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (1_000_000, Decimal(50_000)),
        (2_000_000, Decimal(100_000)),
        (155_770, Decimal("7_788.5")),
        (221_350, Decimal("11_067.5")),
    ],
)
def test_calculate_fixed_tax_without_rounder(
    compensations_tax_rate: Decimal,
    amount: Number,
    expected_tax: Decimal,
) -> None:
    result = calculate_fixed_tax(amount, compensations_tax_rate)

    assert isinstance(result, Decimal)
    assert result == expected_tax


@pytest.mark.parametrize(
    "target, expected_gross",
    [
        (1_000_000, Decimal(1_052_700)),
        (2_000_000, Decimal(2_105_300)),
        (-2_000_000, Decimal(-2_105_200)),
    ],
)
def test_calculate_gross_compensation(
    tax_rounder: Rounder,
    compensations_tax_rate: Decimal,
    target: Number,
    expected_gross: Decimal,
) -> None:
    result = calculate_gross_compensation(
        target, compensations_tax_rate, tax_rounder
    )

    assert isinstance(result, Decimal)
    assert result == expected_gross
