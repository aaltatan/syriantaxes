from decimal import Decimal
from math import ceil

import pytest


class SocialSecurity:
    def __init__(self, min_salary: Decimal) -> None:
        self._min_salary = min_salary

    def calculate_deduction(self, salary: Decimal) -> Decimal:
        deduction = Decimal(salary) * Decimal("0.07")
        return ceil(deduction) # type: ignore  # noqa: PGH003


class OneHundredRounder:
    def round(self, number: Decimal) -> Decimal:
        return Decimal(ceil(number / 100) * 100)


@pytest.fixture()
def tax_rounder() -> OneHundredRounder:
    return OneHundredRounder()


@pytest.fixture()
def ss_obj() -> SocialSecurity:
    return SocialSecurity(Decimal(750_000))


@pytest.fixture()
def brackets() -> list[dict[str, float]]:
    return [
        {"min": 0, "max": 837_000, "rate": 0},
        {"min": 837_000, "max": 850_000, "rate": 0.11},
        {"min": 850_000, "max": 1_100_000, "rate": 0.13},
        {"min": 1_100_000, "max": 25_000_000, "rate": 0.15},
    ]
