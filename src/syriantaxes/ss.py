from dataclasses import dataclass
from decimal import Decimal

from .cast import to_non_negative, to_rate, validated
from .rounder import apply_rounding
from .types import Number, Rounder


@dataclass(frozen=True, init=False)
class SocialSecurity:
    min_salary: Decimal
    deduction_rate: Decimal
    rounder: Rounder | None

    def __init__(
        self,
        min_salary: Number,
        deduction_rate: Number,
        rounder: Rounder | None = None,
    ) -> None:
        object.__setattr__(self, "min_salary", to_non_negative(min_salary))
        object.__setattr__(self, "deduction_rate", to_rate(deduction_rate))
        object.__setattr__(self, "rounder", rounder)

    def calculate_deduction(self, salary: Number) -> Decimal:
        minimum = self.min_salary
        base = validated(salary, lambda number: number >= minimum, f"a salary >= {minimum}")
        return apply_rounding(base * self.deduction_rate, self.rounder)
