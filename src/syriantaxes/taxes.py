from collections.abc import Iterable
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal
from typing import ClassVar, Protocol, TypeAlias, TypedDict

from .cast import cast_to_decimal
from .types import Number, Rounder


class SocialSecurity(Protocol):
    def calculate_deduction(self, salary: Number) -> Decimal: ...


class BracketWithProps(Protocol):
    @property
    def min(self) -> Number: ...

    @property
    def max(self) -> Number: ...

    @property
    def rate(self) -> Number: ...


class BracketWithVars(Protocol):
    min: Number
    max: Number
    rate: Number


class BracketWithClassVars(Protocol):
    min: ClassVar[Number]
    max: ClassVar[Number]
    rate: ClassVar[Number]


class BracketDict(TypedDict):
    min: Number
    max: Number
    rate: Number


Brackets: TypeAlias = (
    Iterable[BracketWithProps]
    | Iterable[BracketWithVars]
    | Iterable[BracketWithClassVars]
    | Iterable[BracketDict]
)


def calculate_fixed_tax(
    amount: Number,
    fixed_tax_rate: Number,
    rounder: Rounder | None = None,
) -> Decimal:
    """Calculate the fixed tax for an amount.

    Args:
        amount (Number): The amount to calculate the tax for.
        fixed_tax_rate (Number): The fixed tax rate.
        rounder (Rounder, optional): The rounder to use for rounding the result. Defaults to None.

    Returns:
        Decimal: The calculated fixed tax.

    """  # noqa: E501
    amount = cast_to_decimal(amount)
    fixed_tax_rate = cast_to_decimal(fixed_tax_rate, lt=0, gt=1)

    if rounder is not None:
        return rounder.round(amount * fixed_tax_rate)

    return amount * fixed_tax_rate


def calculate_gross_compensation(
    target: Number,
    compensations_tax_rate: Number,
    rounder: Rounder | None = None,
) -> Decimal:
    """Calculate the gross compensation for an amount.

    Args:
        target (Number): The amount to calculate the compensation for.
        compensations_tax_rate (Number): The fixed tax rate.
        rounder (Rounder, optional): The rounder to use for rounding the result. Defaults to None.

    Returns:
        Decimal: The calculated gross compensation.

    """  # noqa: E501
    compensations_tax_rate = cast_to_decimal(compensations_tax_rate, lt=0, gt=1)
    target = cast_to_decimal(target)

    gross = target / (1 - compensations_tax_rate)

    if rounder is not None:
        return rounder.round(gross)

    return gross.quantize(Decimal("1.00"), rounding=ROUND_HALF_EVEN)


def calculate_brackets_tax(  # noqa: PLR0913
    amount: Number,
    brackets: Brackets,
    min_allowed_salary: Number,
    rounder: Rounder | None = None,
    ss_obj: SocialSecurity | None = None,
    ss_salary: Number | None = None,
) -> Decimal:
    """Calculate the tax for an amount based on brackets.

    Args:
        amount (Number): The amount to calculate the tax for.
        brackets (Brackets): The brackets to use for calculating the tax.
        min_allowed_salary (Number): The minimum allowed salary.
        rounder (Rounder, optional): The rounder to use for rounding the result. Defaults to None.
        ss_obj (SocialSecurity, optional): The social security object to use for calculating the deduction. Defaults to None.
        ss_salary (Number, optional): The social security salary to use for calculating the deduction. Defaults to None.

    Returns:
        Decimal: The calculated tax.

    """  # noqa: E501
    amount = cast_to_decimal(amount)
    min_allowed_salary = cast_to_decimal(min_allowed_salary)

    tax = Decimal(0)

    if amount <= min_allowed_salary:
        return tax

    if ss_obj is not None:
        ss_salary = ss_salary or amount
        ss_salary = cast_to_decimal(ss_salary, lt=0)
        taxable_salary = amount - ss_obj.calculate_deduction(ss_salary)
    else:
        taxable_salary = amount

    for bracket in brackets:
        is_dict = isinstance(bracket, dict)

        bracket_min = bracket["min"] if is_dict else bracket.min
        bracket_max = bracket["max"] if is_dict else bracket.max
        bracket_rate = bracket["rate"] if is_dict else bracket.rate

        bracket_min = cast_to_decimal(bracket_min, lt=0)
        bracket_max = cast_to_decimal(bracket_max, lte=bracket_min)
        bracket_rate = cast_to_decimal(bracket_rate, lt=0, gt=1)

        if bracket_min <= taxable_salary <= bracket_max:
            bracket_tax = bracket_rate * (taxable_salary - bracket_min)
            tax += bracket_tax

            if rounder is not None:
                return rounder.round(tax)

            return tax

        tax += (bracket_max - bracket_min) * bracket_rate

    return tax


def calculate_gross_salary(
    target: Number,
    brackets: Brackets,
    min_allowed_salary: Number,
    rounder: Rounder | None = None,
    max_amount_ratio: Number = 1.5,
) -> Decimal:
    """Calculate the gross fixed salary for an amount based on brackets.

    Args:
        target (Number): The amount to calculate the gross fixed salary for.
        brackets (Brackets): The brackets to use for calculating the tax.
        min_allowed_salary (Number): The minimum allowed salary.
        rounder (Rounder, optional): The rounder to use for rounding the result. Defaults to None.
        max_amount_ratio (Number, optional): The maximum amount ratio. Defaults to 1.5.

    Returns:
        Decimal: The calculated gross fixed salary.

    """  # noqa: E501
    target = cast_to_decimal(target)
    min_allowed_salary = cast_to_decimal(min_allowed_salary)

    if target < min_allowed_salary:
        message = (
            f"Can't be calculated for salary less than {min_allowed_salary}."
        )
        raise ValueError(message)

    if (
        calculate_brackets_tax(target, brackets, min_allowed_salary, rounder)
        == 0
    ):
        return target

    max_amount_ratio = cast_to_decimal(max_amount_ratio, lt=0)

    min_amount = Decimal(target)
    max_amount = (target * max_amount_ratio).to_integral(rounding=ROUND_DOWN)

    while True:
        mid_amount = ((min_amount + max_amount) / 2).to_integral(
            rounding=ROUND_DOWN
        )
        mid_net = mid_amount - calculate_brackets_tax(
            mid_amount, brackets, min_allowed_salary, rounder
        )

        if mid_net > target:
            max_amount = mid_amount
        elif mid_net < target:
            min_amount = mid_amount
        else:
            return mid_amount


def calculate_gross_components(  # noqa: PLR0913
    target: Number,
    compensations_rate: Number,
    brackets: Brackets,
    min_allowed_salary: Number,
    compensations_tax_rate: Number,
    rounder: Rounder | None = None,
) -> tuple[Decimal, Decimal]:
    """Calculate the gross components for an amount based on brackets.

    Args:
        target (Number): The amount to calculate the gross components for.
        compensations_rate (Number | float): The compensations rate.
        brackets (Brackets): The brackets to use for calculating the tax.
        min_allowed_salary (Number): The minimum allowed salary.
        compensations_tax_rate (Number): The compensations tax rate.
        rounder (Rounder, optional): The rounder to use for rounding the result. Defaults to None.

    Returns:
        tuple[Decimal, Decimal]: A tuple containing the gross salary and compensations.

    """  # noqa: E501
    compensations_rate = cast_to_decimal(compensations_rate, lt=0, gt=1)
    target = cast_to_decimal(target)
    min_allowed_salary = cast_to_decimal(min_allowed_salary)

    if target < min_allowed_salary:
        message = (
            f"Can't be calculated for salary less than {min_allowed_salary}."
        )
        raise ValueError(message)

    gross_salary_before = Decimal(
        target * (1 - compensations_rate)
    ).to_integral(rounding=ROUND_DOWN)

    if gross_salary_before < min_allowed_salary:
        gross_salary = min_allowed_salary
        minium_salary_tax = calculate_brackets_tax(
            min_allowed_salary, brackets, min_allowed_salary, rounder
        )
        compensations_before = target - min_allowed_salary + minium_salary_tax
    else:
        gross_salary = calculate_gross_salary(
            gross_salary_before, brackets, min_allowed_salary, rounder
        )
        compensations_before = target - gross_salary_before

    compensations = calculate_gross_compensation(
        compensations_before, compensations_tax_rate, rounder
    )

    return (gross_salary, compensations)
