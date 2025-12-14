# ruff: noqa: S101

from decimal import Decimal

import pytest
from syriantaxes import (
    Bracket,
    Rounder,
    SocialSecurity,
    calculate_brackets_tax,
    calculate_fixed_tax,
    calculate_gross_compensation,
    # calculate_gross_components,
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


@pytest.mark.parametrize(
    "target, expected_gross",
    [
        (650_300, Decimal("684_526.32")),
        (277_550, Decimal("292_157.89")),
        (241_241, Decimal("253_937.89")),
        (-241_241, Decimal("-253_937.89")),
    ],
)
def test_calculate_gross_compensation_without_rounder(
    compensations_tax_rate: Decimal,
    target: Number,
    expected_gross: Decimal,
) -> None:
    result = calculate_gross_compensation(target, compensations_tax_rate)

    assert isinstance(result, Decimal)
    assert result == expected_gross


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (500_000, Decimal(0)),
        (1_000_000, Decimal(21_000)),
        (1_220_300, Decimal(52_000)),
        (1_221_000, Decimal(52_100)),
        (2_000_000, Decimal(169_000)),
        (5_250_250, Decimal(656_500)),
    ],
)
def test_calculate_brackets_tax_without_ss(
    brackets: list[Bracket],
    min_allowed_salary: Number,
    tax_rounder: Rounder,
    amount: Number,
    expected_tax: Decimal,
) -> None:
    tax = calculate_brackets_tax(
        amount, brackets, min_allowed_salary, tax_rounder
    )

    assert isinstance(tax, Decimal)
    assert tax == expected_tax


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (880_962, Decimal("5455.06")),
        (1_000_000, Decimal(20_930)),
        (2_000_000, Decimal(168_930)),
    ],
)
def test_calculate_brackets_tax_without_rounder(
    brackets: list[Bracket],
    min_allowed_salary: Number,
    amount: Number,
    expected_tax: Decimal,
) -> None:
    tax = calculate_brackets_tax(amount, brackets, min_allowed_salary)

    assert isinstance(tax, Decimal)
    assert tax == expected_tax


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (500_000, Decimal(0)),
        (1_000_000, Decimal(0)),
        (2_000_000, Decimal(0)),
    ],
)
def test_calculate_brackets_tax_without_brackets(
    min_allowed_salary: Number,
    amount: Number,
    expected_tax: Decimal,
) -> None:
    tax = calculate_brackets_tax(amount, [], min_allowed_salary)

    assert isinstance(tax, Decimal)
    assert tax == expected_tax


@pytest.mark.parametrize(
    "amount, ss_salary, expected_tax",
    [
        (1_000_000, 750_000, Decimal(14_200)),
        (1_220_300, 1_000_000, Decimal(41_500)),
        (1_221_000, 1_000_000, Decimal(41_600)),
        (2_000_000, 1_500_000, Decimal(153_200)),
        (5_250_250, 2_000_000, Decimal(635_500)),
    ],
)
def test_calculate_brackets_tax_with_ss(  # noqa: PLR0913
    brackets: list[Bracket],
    tax_rounder: Rounder,
    ss_obj: SocialSecurity,
    min_allowed_salary: Number,
    amount: Number,
    ss_salary: Number,
    expected_tax: Decimal,
) -> None:
    tax = calculate_brackets_tax(
        amount=amount,
        brackets=brackets,
        min_allowed_salary=min_allowed_salary,
        rounder=tax_rounder,
        ss_obj=ss_obj,
        ss_salary=ss_salary,
    )

    assert isinstance(tax, Decimal)
    assert tax == expected_tax


def test_calculate_gross_salary_under_min_allowed_salary(
    brackets: list[Bracket], min_allowed_salary: Number, tax_rounder: Rounder
) -> None:
    with pytest.raises(ValueError):
        target = Decimal(min_allowed_salary) - 1
        calculate_gross_salary(
            target=target,
            brackets=brackets,
            min_allowed_salary=min_allowed_salary,
            rounder=tax_rounder,
        )


@pytest.mark.parametrize(
    "target, expected_gross",
    [
        (837_000, Decimal(837_000)),
        (1_000_000, Decimal(1_024_100)),
        (1_712_500, Decimal(1_860_600)),
        (2_000_000, Decimal(2_198_800)),
        (2_224_700, Decimal(2_463_200)),
        (4_350_000, Decimal(4_963_500)),
    ],
)
def test_calculate_gross_salary(
    brackets: list[Bracket],
    min_allowed_salary: Number,
    tax_rounder: Rounder,
    target: Number,
    expected_gross: Decimal,
):
    gross_salary = calculate_gross_salary(
        target, brackets, min_allowed_salary, tax_rounder
    )

    assert isinstance(gross_salary, Decimal)
    assert gross_salary == expected_gross


@pytest.mark.parametrize(
    "target, expected_gross",
    [
        (837_000, Decimal(837_000)),
        (1_000_000, Decimal(1_024_058)),
        (1_712_500, Decimal(1_860_506)),
        (2_000_000, Decimal(2_198_741)),
        (2_224_700, Decimal(2_463_094)),
        (4_350_000, Decimal(4_963_447)),
    ],
)
def test_calculate_gross_salary_without_rounder(
    brackets: list[Bracket],
    min_allowed_salary: Number,
    target: Number,
    expected_gross: Decimal,
):
    gross_salary = calculate_gross_salary(target, brackets, min_allowed_salary)

    assert isinstance(gross_salary, Decimal)
    assert gross_salary == expected_gross


# TODO: test for calculate_gross_components  # noqa: FIX002, TD002, TD003
