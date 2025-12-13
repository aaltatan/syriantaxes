from decimal import Decimal

import pytest


@pytest.fixture()
def min_allowed_salary() -> Decimal:
    return Decimal(837_000)


@pytest.fixture()
def compensations_tax_rate() -> Decimal:
    return Decimal("0.05")


@pytest.fixture()
def compensations_rate() -> Decimal:
    return Decimal("0.75")
