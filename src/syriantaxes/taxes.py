from collections.abc import Callable
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal

from .bracket import Bracket, bracket_tax, to_bracket
from .cast import to_decimal, to_positive, to_rate
from .rounder import TO_CENTS, apply_rounding
from .types import Brackets, DeductionCalculator, Number, Rounder


class SalaryBelowMinimumError(ValueError):
    def __init__(self, min_allowed_salary: Decimal) -> None:
        super().__init__(f"Can't be calculated for salary less than {min_allowed_salary}.")


class NoExactGrossSalaryError(ValueError):
    def __init__(self, target: Decimal) -> None:
        super().__init__(f"No whole-number gross salary has a net of exactly {target}.")


def calculate_fixed_tax(
    amount: Number,
    fixed_tax_rate: Number,
    rounder: Rounder | None = None,
) -> Decimal:
    """Calculate a flat-rate tax on amount."""
    tax = to_decimal(amount) * to_rate(fixed_tax_rate)
    return apply_rounding(tax, rounder)


def calculate_gross_compensation(
    target: Number,
    compensations_tax_rate: Number,
    rounder: Rounder | None = None,
) -> Decimal:
    """Calculate the compensation that leaves target after the flat compensations tax.

    Without a rounder the result is rounded half-even to two decimal places.
    """
    gross = to_decimal(target) / (1 - to_rate(compensations_tax_rate))
    return (rounder or TO_CENTS).round(gross)


def calculate_brackets_tax(  # noqa: PLR0913
    amount: Number,
    brackets: Brackets,
    min_allowed_salary: Number,  # noqa: ARG001 - kept for API compatibility
    rounder: Rounder | None = None,
    ss_obj: DeductionCalculator | None = None,
    *,
    ss_salary: Number | None = None,
) -> Decimal:
    """Calculate the progressive tax on amount.

    Args:
        amount: The salary to tax.
        brackets: The tax brackets, in any supported shape.
        min_allowed_salary: The minimum allowed salary. Currently unused.
        rounder: Rounds the final tax. Defaults to no rounding.
        ss_obj: Calculates the social security deduction taken off before taxing.
        ss_salary: The salary the social security deduction is based on. Defaults to amount.

    """
    taxable_salary = _taxable_salary(to_decimal(amount), ss_obj, ss_salary)
    tax = sum((bracket_tax(to_bracket(b), taxable_salary) for b in brackets), Decimal(0))
    return apply_rounding(tax, rounder)


def calculate_gross_salary(
    target: Number,
    brackets: Brackets,
    min_allowed_salary: Number,
    rounder: Rounder | None = None,
    max_amount_ratio: Number = 1.5,
) -> Decimal:
    """Find the whole-number gross salary whose net (after bracket tax) equals target.

    Args:
        target: The net salary wanted.
        brackets: The tax brackets, in any supported shape.
        min_allowed_salary: The lowest target allowed.
        rounder: Rounds the tax. Without one, the net is rounded half-even to a whole number.
        max_amount_ratio: Upper bound of the search, as a multiple of target.

    Raises:
        SalaryBelowMinimumError: If target is below min_allowed_salary.
        NoExactGrossSalaryError: If no whole-number gross salary gives exactly target.

    """
    net_target = to_decimal(target)
    min_salary = to_decimal(min_allowed_salary)
    upper = (net_target * to_positive(max_amount_ratio)).to_integral_value(ROUND_DOWN)
    _require_min_salary(net_target, min_salary)

    tax_brackets = _to_brackets(brackets)

    def tax(salary: Decimal) -> Decimal:
        return calculate_brackets_tax(salary, tax_brackets, min_salary, rounder)

    def net_salary(gross: Decimal) -> Decimal:
        net = gross - tax(gross)
        return net if rounder is not None else net.to_integral_value(ROUND_HALF_EVEN)

    if tax(net_target) == 0:
        return net_target

    return _search_gross(net_salary, net_target, net_target, upper)


def calculate_gross_components(  # noqa: PLR0913
    target: Number,
    compensations_rate: Number,
    brackets: Brackets,
    min_allowed_salary: Number,
    compensations_tax_rate: Number,
    *,
    rounder: Rounder | None = None,
) -> tuple[Decimal, Decimal]:
    """Split a net target into a gross salary and a gross compensation.

    Args:
        target: The total net amount wanted.
        compensations_rate: The share of target paid as compensation.
        brackets: The tax brackets, in any supported shape.
        min_allowed_salary: The lowest salary allowed.
        compensations_tax_rate: The flat tax rate on compensation.
        rounder: Rounds the taxes and the compensation.

    Returns:
        The gross salary and the gross compensation.

    Raises:
        SalaryBelowMinimumError: If target is below min_allowed_salary.

    """
    total = to_decimal(target)
    min_salary = to_decimal(min_allowed_salary)
    compensation_tax_rate = to_rate(compensations_tax_rate)
    _require_min_salary(total, min_salary)

    tax_brackets = _to_brackets(brackets)
    net_salary = (total * (1 - to_rate(compensations_rate))).to_integral_value(ROUND_DOWN)

    if net_salary < min_salary:
        gross_salary = min_salary
        min_salary_tax = calculate_brackets_tax(min_salary, tax_brackets, min_salary, rounder)
        net_compensation = total - min_salary + min_salary_tax
    else:
        gross_salary = calculate_gross_salary(net_salary, tax_brackets, min_salary, rounder)
        net_compensation = total - net_salary

    gross_compensation = calculate_gross_compensation(
        net_compensation, compensation_tax_rate, rounder
    )

    return gross_salary, gross_compensation


def _require_min_salary(salary: Decimal, min_allowed_salary: Decimal) -> None:
    if salary < min_allowed_salary:
        raise SalaryBelowMinimumError(min_allowed_salary)


def _to_brackets(brackets: Brackets) -> list[Bracket]:
    # A list, unlike a generator, can be read again on every tax calculation.
    return [to_bracket(bracket) for bracket in brackets]


def _taxable_salary(
    amount: Decimal,
    ss_obj: DeductionCalculator | None,
    ss_salary: Number | None,
) -> Decimal:
    if ss_obj is None:
        return amount

    return amount - ss_obj.calculate_deduction(to_decimal(ss_salary or amount))


def _search_gross(
    net_salary: Callable[[Decimal], Decimal],
    target: Decimal,
    low: Decimal,
    high: Decimal,
) -> Decimal:
    """Binary-search [low, high) for the whole-number gross whose net equals target."""
    mid = ((low + high) / 2).to_integral_value(ROUND_DOWN)
    mid_net = net_salary(mid)

    if mid_net == target:
        return mid

    if high - low <= 1:
        raise NoExactGrossSalaryError(target)

    if mid_net > target:
        return _search_gross(net_salary, target, low, mid)

    return _search_gross(net_salary, target, mid, high)
