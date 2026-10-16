from decimal import Decimal
from typing import ClassVar

import pytest

from syriantaxes import (
    NoExactGrossSalaryError,
    SalaryBelowMinimumError,
    calculate_brackets_tax,
    calculate_gross_salary,
)


class AttributeBracket:
    def __init__(self, _min: int, _max: int, rate: float) -> None:
        self.min = _min
        self.max = _max
        self.rate = rate


class FirstBracket:
    min: ClassVar[int] = 0
    max: ClassVar[int] = 837_000
    rate: ClassVar[float] = 0


@pytest.fixture()
def attribute_brackets() -> list[AttributeBracket]:
    return [
        AttributeBracket(0, 837_000, 0),
        AttributeBracket(837_000, 850_000, 0.11),
        AttributeBracket(850_000, 1_100_000, 0.13),
        AttributeBracket(1_100_000, 25_000_000, 0.15),
    ]


def test_calculate_brackets_tax_with_attribute_brackets(
    attribute_brackets: list[AttributeBracket], min_allowed_salary: Decimal
) -> None:
    tax = calculate_brackets_tax(1_000_000, attribute_brackets, min_allowed_salary)

    assert tax == Decimal(20_930)


def test_calculate_brackets_tax_with_class_var_brackets(min_allowed_salary: Decimal) -> None:
    tax = calculate_brackets_tax(500_000, [FirstBracket()], min_allowed_salary)

    assert tax == Decimal(0)


def test_calculate_gross_salary_accepts_a_generator(
    attribute_brackets: list[AttributeBracket], min_allowed_salary: Decimal
) -> None:
    brackets = (bracket for bracket in attribute_brackets)

    gross_salary = calculate_gross_salary(1_000_000, brackets, min_allowed_salary)

    assert gross_salary == Decimal(1_024_058)


def test_salary_below_minimum_error_is_a_value_error(
    attribute_brackets: list[AttributeBracket], min_allowed_salary: Decimal
) -> None:
    with pytest.raises(SalaryBelowMinimumError) as error:
        calculate_gross_salary(min_allowed_salary - 1, attribute_brackets, min_allowed_salary)

    assert isinstance(error.value, ValueError)


def test_calculate_gross_salary_raises_when_no_gross_gives_the_target(
    min_allowed_salary: Decimal,
) -> None:
    brackets = [AttributeBracket(0, 837_000, 0), AttributeBracket(837_000, 25_000_000, 1)]

    with pytest.raises(NoExactGrossSalaryError):
        calculate_gross_salary(900_000, brackets, min_allowed_salary)
