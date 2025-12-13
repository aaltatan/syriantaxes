from decimal import Decimal

import pytest
from syriantaxes import Bracket, Rounder, RoundingMethod, SocialSecurity


@pytest.fixture()
def tax_rounder() -> Rounder:
    return Rounder(RoundingMethod.CEILING, 100)


@pytest.fixture()
def ss_rounder() -> Rounder:
    return Rounder(RoundingMethod.CEILING, 1)


@pytest.fixture()
def ss_obj(ss_rounder: Rounder) -> SocialSecurity:
    return SocialSecurity(Decimal(750_000), Decimal("0.07"), ss_rounder)


@pytest.fixture()
def brackets() -> list[Bracket]:
    return [
        Bracket(0, 837_000, 0),
        Bracket(837_000, 850_000, 0.11),
        Bracket(850_000, 1_100_000, 0.13),
        Bracket(1_100_000, 25_000_000, 0.15),
    ]
