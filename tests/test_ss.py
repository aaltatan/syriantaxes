# ruff: noqa: S101

from decimal import Decimal

import pytest
from syriantaxes import Rounder, RoundingMethod, SocialSecurity
from syriantaxes.types import Number


@pytest.fixture()
def rounder() -> Rounder:
    return Rounder(RoundingMethod.CEILING, 1)


@pytest.fixture()
def deduction_rate() -> Decimal:
    return Decimal("0.07")


@pytest.fixture()
def min_ss_allowed_salary() -> Decimal:
    return Decimal(750_000)


@pytest.fixture()
def ss(
    rounder: Rounder,
    deduction_rate: Decimal,
    min_ss_allowed_salary: Decimal,
) -> SocialSecurity:
    return SocialSecurity(min_ss_allowed_salary, deduction_rate, rounder)


@pytest.fixture()
def ss_without_rounder(
    deduction_rate: Decimal, min_ss_allowed_salary: Decimal
) -> SocialSecurity:
    return SocialSecurity(min_ss_allowed_salary, deduction_rate)


@pytest.mark.parametrize(
    "salary, deduction",
    [
        (750_000, Decimal(52_500)),
        (817_500, Decimal(57_225)),
        (891_075, Decimal(62_376)),
        (837_000, Decimal(58_590)),
        (1_000_000, Decimal(70_000)),
        (2_000_000, Decimal(140_000)),
    ],
)
def test_ss_with_rounder_calculate_deduction(
    ss: SocialSecurity, salary: Number, deduction: Decimal
) -> None:
    result = ss.calculate_deduction(salary)

    assert isinstance(ss.min_salary, Decimal)
    assert isinstance(ss.deduction_rate, Decimal)
    assert isinstance(result, Decimal)

    assert (
        str(ss)
        == f"SocialSecurity(min_salary={ss.min_salary}, deduction_rate={ss.deduction_rate})"  # noqa: E501
    )
    assert result == deduction


@pytest.mark.parametrize(
    "salary, deduction",
    [
        (750_000, Decimal(52_500)),
        (817_500, Decimal(57_225)),
        (891_075, Decimal("62_375.25")),
        (837_000, Decimal(58_590)),
        (1_000_000, Decimal(70_000)),
        (2_000_000, Decimal(140_000)),
    ],
)
def test_ss_without_rounder_calculate_deduction(
    ss_without_rounder: SocialSecurity,
    salary: Number,
    deduction: Decimal,
) -> None:
    result = ss_without_rounder.calculate_deduction(salary)

    assert isinstance(ss_without_rounder.min_salary, Decimal)
    assert isinstance(ss_without_rounder.deduction_rate, Decimal)
    assert isinstance(result, Decimal)
    assert result == deduction


def test_ss_with_invalid_salary(
    ss: SocialSecurity, min_ss_allowed_salary: Decimal
) -> None:
    with pytest.raises(ValueError):
        ss.calculate_deduction(min_ss_allowed_salary - 1)


def test_init_with_invalid_args(min_ss_allowed_salary: Decimal) -> None:
    with pytest.raises(ValueError):
        SocialSecurity(min_ss_allowed_salary, -0.1)

    with pytest.raises(ValueError):
        SocialSecurity(min_ss_allowed_salary, 1.1)

    with pytest.raises(ValueError):
        SocialSecurity(Decimal(-1_000_000), 0.5)


def test_init_with_invalid_setter(ss: SocialSecurity) -> None:
    with pytest.raises(ValueError):
        ss.min_salary = Decimal(-1_000_000)

    with pytest.raises(ValueError):
        ss.deduction_rate = Decimal("-0.1")

    with pytest.raises(ValueError):
        ss.deduction_rate = Decimal("1.1")
