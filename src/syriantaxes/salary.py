from collections.abc import Iterator
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal
from itertools import count

from .rules import Bracket, TaxRules


class SalaryBelowMinimumError(ValueError):
    def __init__(self, min_salary: Decimal) -> None:
        super().__init__(f"Can't be calculated for salary less than {min_salary}.")


@dataclass(frozen=True)
class SalaryBreakdown:
    gross: Decimal
    social_security: Decimal
    taxable: Decimal
    tax: Decimal

    @property
    def net(self) -> Decimal:
        return self.gross - self.social_security - self.tax


def social_security_deduction(rules: TaxRules, insured_salary: Decimal) -> Decimal:
    social_security = rules.social_security

    if social_security is None:
        return Decimal(0)

    if insured_salary < social_security.min_salary:
        message = (
            f"insured salary must be at least {social_security.min_salary}, got {insured_salary}"
        )
        raise ValueError(message)

    return social_security.rounding(insured_salary * social_security.rate)


def salary_breakdown(
    rules: TaxRules, gross: Decimal, *, insured_salary: Decimal | None = None
) -> SalaryBreakdown:
    """Work out social security, taxable salary, tax and net for a gross salary.

    Social security is based on insured_salary, which defaults to the gross salary.
    """
    insured = gross if insured_salary is None else insured_salary
    social_security = social_security_deduction(rules, insured)
    taxable = gross - social_security
    tax = rules.rounding(_bracket_tax(rules.brackets, taxable))

    return SalaryBreakdown(gross, social_security, taxable, tax)


def salary_tax(
    rules: TaxRules, gross: Decimal, *, insured_salary: Decimal | None = None
) -> Decimal:
    return salary_breakdown(rules, gross, insured_salary=insured_salary).tax


def gross_salary(rules: TaxRules, net: Decimal) -> Decimal:
    """Find the gross salary whose net, after social security and tax, reaches net.

    Returns the first whole gross, counting up from the exact unrounded answer, whose net is at
    least net. Social security is based on the gross salary itself.
    """
    if net < rules.min_salary:
        raise SalaryBelowMinimumError(rules.min_salary)

    start = _unrounded_gross(rules, net).to_integral_value(ROUND_FLOOR)
    candidates = (start + extra for extra in count())

    return next(gross for gross in candidates if salary_breakdown(rules, gross).net >= net)


def _unrounded_gross(rules: TaxRules, net: Decimal) -> Decimal:
    social_security_rate = (
        Decimal(0) if rules.social_security is None else rules.social_security.rate
    )
    return _taxable_for_net(rules.brackets, net) / (1 - social_security_rate)


def _bracket_tax(brackets: tuple[Bracket, ...], taxable: Decimal) -> Decimal:
    """Progressive tax on taxable, before rounding."""
    return sum(
        (
            bracket.rate * _part_in_band(taxable, bracket.lower, upper)
            for bracket, upper in _bands(brackets)
        ),
        Decimal(0),
    )


def _taxable_for_net(brackets: tuple[Bracket, ...], net: Decimal) -> Decimal:
    """Solve taxable - tax(taxable) == net, without rounding.

    Within one band that is a straight line, so find the band net falls in and solve it.
    """
    bracket = next(
        bracket
        for bracket, upper in _bands(brackets)
        if upper is None or net <= upper - _bracket_tax(brackets, upper)
    )
    net_at_lower = bracket.lower - _bracket_tax(brackets, bracket.lower)

    return bracket.lower + (net - net_at_lower) / (1 - bracket.rate)


def _bands(brackets: tuple[Bracket, ...]) -> Iterator[tuple[Bracket, Decimal | None]]:
    """Pair each bracket with its upper limit: the next bracket's lower, or None for the last."""
    uppers: list[Decimal | None] = [bracket.lower for bracket in brackets[1:]]
    return zip(brackets, [*uppers, None], strict=True)


def _part_in_band(amount: Decimal, lower: Decimal, upper: Decimal | None) -> Decimal:
    top = amount if upper is None else min(amount, upper)
    return max(top - lower, Decimal(0))
