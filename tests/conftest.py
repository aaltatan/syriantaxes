from decimal import ROUND_CEILING, Decimal

import pytest

from syriantaxes import Bracket, SocialSecurity, TaxRules, round_to

BRACKETS = (
    Bracket(Decimal(0), Decimal(0)),
    Bracket(Decimal(837_000), Decimal("0.11")),
    Bracket(Decimal(850_000), Decimal("0.13")),
    Bracket(Decimal(1_100_000), Decimal("0.15")),
)

SOCIAL_SECURITY = SocialSecurity(
    rate=Decimal("0.07"),
    min_salary=Decimal(750_000),
    rounding=round_to(Decimal(1), ROUND_CEILING),
)


@pytest.fixture()
def rules() -> TaxRules:
    """Taxes rounded up to the nearest 100, no social security."""
    return TaxRules(
        brackets=BRACKETS,
        min_salary=Decimal(837_000),
        compensation_tax_rate=Decimal("0.05"),
        rounding=round_to(Decimal(100), ROUND_CEILING),
    )


@pytest.fixture()
def cent_rules() -> TaxRules:
    """Default rounding (half-even to the cent), no social security."""
    return TaxRules(
        brackets=BRACKETS,
        min_salary=Decimal(837_000),
        compensation_tax_rate=Decimal("0.05"),
    )


@pytest.fixture()
def rules_with_ss(rules: TaxRules) -> TaxRules:
    return TaxRules(
        brackets=rules.brackets,
        min_salary=rules.min_salary,
        compensation_tax_rate=rules.compensation_tax_rate,
        rounding=rules.rounding,
        social_security=SOCIAL_SECURITY,
    )
