from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from syriantaxes import Bracket, SocialSecurity, TaxRules


@pytest.mark.parametrize(
    "lower, rate",
    [
        (Decimal(-1), Decimal("0.1")),
        (Decimal(0), Decimal("-0.1")),
        (Decimal(0), Decimal(1)),
    ],
)
def test_bracket_rejects_invalid_values(lower: Decimal, rate: Decimal) -> None:
    with pytest.raises(ValueError):
        Bracket(lower, rate)


@pytest.mark.parametrize(
    "rate, min_salary",
    [
        (Decimal("-0.07"), Decimal(750_000)),
        (Decimal(1), Decimal(750_000)),
        (Decimal("0.07"), Decimal(-1)),
    ],
)
def test_social_security_rejects_invalid_values(rate: Decimal, min_salary: Decimal) -> None:
    with pytest.raises(ValueError):
        SocialSecurity(rate, min_salary)


@pytest.mark.parametrize(
    "brackets",
    [
        (),
        (Bracket(Decimal(100), Decimal(0)),),
        (Bracket(Decimal(0), Decimal(0)), Bracket(Decimal(0), Decimal("0.1"))),
        (
            Bracket(Decimal(0), Decimal(0)),
            Bracket(Decimal(500), Decimal("0.1")),
            Bracket(Decimal(400), Decimal("0.2")),
        ),
    ],
)
def test_rules_reject_invalid_brackets(rules: TaxRules, brackets: tuple[Bracket, ...]) -> None:
    with pytest.raises(ValueError, match="brackets"):
        replace(rules, brackets=brackets)


def test_rules_reject_a_negative_min_salary(rules: TaxRules) -> None:
    with pytest.raises(ValueError, match="min_salary"):
        replace(rules, min_salary=Decimal(-1))


def test_rules_reject_an_invalid_compensation_tax_rate(rules: TaxRules) -> None:
    with pytest.raises(ValueError, match="compensation_tax_rate"):
        replace(rules, compensation_tax_rate=Decimal(1))


def test_rules_are_immutable(rules: TaxRules) -> None:
    with pytest.raises(FrozenInstanceError):
        rules.min_salary = Decimal(0)  # type: ignore[misc]
