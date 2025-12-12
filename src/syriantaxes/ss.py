from decimal import Decimal

from .cast import cast_to_decimal
from .types import Number, Rounder


class SocialSecurity:
    def __init__(
        self,
        min_salary: Number,
        deduction_rate: Number,
        rounder: Rounder | None = None,
    ) -> None:
        self._min_salary = cast_to_decimal(min_salary, lt=0)
        self._deduction_rate = cast_to_decimal(deduction_rate, lt=0, gt=1)
        self.rounder = rounder

    @property
    def min_salary(self) -> Decimal:
        return self._min_salary

    @min_salary.setter
    def min_salary(self, value: Number) -> None:
        self._min_salary = cast_to_decimal(value, lt=0)

    @property
    def deduction_rate(self) -> Decimal:
        return self._deduction_rate

    @deduction_rate.setter
    def deduction_rate(self, value: Number) -> None:
        self._deduction_rate = cast_to_decimal(value, lt=0, gt=1)

    def calculate_deduction(self, salary: Number) -> Decimal:
        salary = cast_to_decimal(salary, lt=self._min_salary)
        result = salary * self._deduction_rate

        if self.rounder is not None:
            return self.rounder.round(result)

        return result

    def __repr__(self) -> str:
        return f"SocialSecurity(min_salary={self._min_salary}, deduction_rate={self._deduction_rate})"  # noqa: E501
