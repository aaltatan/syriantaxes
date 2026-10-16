from dataclasses import dataclass
from decimal import Decimal
from itertools import pairwise

from .rounding import Rounding, to_cents


@dataclass(frozen=True)
class Bracket:
    """A tax band from lower up to the next bracket's lower (the last one has no top)."""

    lower: Decimal
    rate: Decimal

    def __post_init__(self) -> None:
        _check_not_negative(self.lower, "lower")
        _check_rate(self.rate, "rate")


@dataclass(frozen=True)
class SocialSecurity:
    rate: Decimal
    min_salary: Decimal
    rounding: Rounding = to_cents

    def __post_init__(self) -> None:
        _check_rate(self.rate, "rate")
        _check_not_negative(self.min_salary, "min_salary")


@dataclass(frozen=True)
class TaxRules:
    """Everything the law fixes for one period: brackets, rates and rounding."""

    brackets: tuple[Bracket, ...]
    min_salary: Decimal
    compensation_tax_rate: Decimal
    social_security: SocialSecurity | None = None
    rounding: Rounding = to_cents

    def __post_init__(self) -> None:
        lowers = [bracket.lower for bracket in self.brackets]

        if not lowers or lowers[0] != 0:
            message = "brackets must start with a bracket whose lower is 0"
            raise ValueError(message)

        if any(lower >= upper for lower, upper in pairwise(lowers)):
            message = "brackets must be in strictly increasing order of lower"
            raise ValueError(message)

        _check_not_negative(self.min_salary, "min_salary")
        _check_rate(self.compensation_tax_rate, "compensation_tax_rate")


def _check_rate(rate: Decimal, name: str) -> None:
    # A rate of 1 or more would leave nothing after tax, so no gross could be found.
    if not 0 <= rate < 1:
        message = f"{name} must be at least 0 and below 1, got {rate}"
        raise ValueError(message)


def _check_not_negative(value: Decimal, name: str) -> None:
    if value < 0:
        message = f"{name} must be >= 0, got {value}"
        raise ValueError(message)
