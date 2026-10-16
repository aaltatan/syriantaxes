from dataclasses import replace
from decimal import Decimal

import pytest

from syriantaxes import (
    Bracket,
    SalaryBelowMinimumError,
    SalaryBreakdown,
    TaxRules,
    gross_salary,
    salary_breakdown,
    salary_tax,
    social_security_deduction,
)


@pytest.mark.parametrize(
    "gross, expected_tax",
    [
        (Decimal(500_000), Decimal(0)),
        (Decimal(1_000_000), Decimal(21_000)),
        (Decimal(1_220_300), Decimal(52_000)),
        (Decimal(1_221_000), Decimal(52_100)),
        (Decimal(2_000_000), Decimal(169_000)),
        (Decimal(5_250_250), Decimal(656_500)),
    ],
)
def test_salary_tax(rules: TaxRules, gross: Decimal, expected_tax: Decimal) -> None:
    assert salary_tax(rules, gross) == expected_tax


@pytest.mark.parametrize(
    "gross, expected_tax",
    [
        (Decimal(880_962), Decimal("5455.06")),
        (Decimal(1_000_000), Decimal(20_930)),
        (Decimal(2_000_000), Decimal(168_930)),
    ],
)
def test_salary_tax_to_the_cent(
    cent_rules: TaxRules, gross: Decimal, expected_tax: Decimal
) -> None:
    assert salary_tax(cent_rules, gross) == expected_tax


@pytest.mark.parametrize("gross", [Decimal(500_000), Decimal(1_000_000), Decimal(2_000_000)])
def test_salary_tax_with_a_single_tax_free_bracket(rules: TaxRules, gross: Decimal) -> None:
    tax_free = replace(rules, brackets=(Bracket(Decimal(0), Decimal(0)),))

    assert salary_tax(tax_free, gross) == 0


@pytest.mark.parametrize(
    "gross, insured_salary, expected_tax",
    [
        (Decimal(1_000_000), Decimal(750_000), Decimal(14_200)),
        (Decimal(1_220_300), Decimal(1_000_000), Decimal(41_500)),
        (Decimal(1_221_000), Decimal(1_000_000), Decimal(41_600)),
        (Decimal(2_000_000), Decimal(1_500_000), Decimal(153_200)),
        (Decimal(5_250_250), Decimal(2_000_000), Decimal(635_500)),
    ],
)
def test_salary_tax_after_social_security(
    rules_with_ss: TaxRules, gross: Decimal, insured_salary: Decimal, expected_tax: Decimal
) -> None:
    assert salary_tax(rules_with_ss, gross, insured_salary=insured_salary) == expected_tax


@pytest.mark.parametrize(
    "insured_salary, expected_deduction",
    [
        (Decimal(750_000), Decimal(52_500)),
        (Decimal(817_500), Decimal(57_225)),
        (Decimal(891_075), Decimal(62_376)),
        (Decimal(837_000), Decimal(58_590)),
        (Decimal(1_000_000), Decimal(70_000)),
        (Decimal(2_000_000), Decimal(140_000)),
    ],
)
def test_social_security_deduction(
    rules_with_ss: TaxRules, insured_salary: Decimal, expected_deduction: Decimal
) -> None:
    assert social_security_deduction(rules_with_ss, insured_salary) == expected_deduction


def test_social_security_deduction_to_the_cent(rules_with_ss: TaxRules) -> None:
    assert rules_with_ss.social_security is not None
    unrounded = replace(rules_with_ss.social_security, rounding=lambda amount: amount)
    rules = replace(rules_with_ss, social_security=unrounded)

    assert social_security_deduction(rules, Decimal(891_075)) == Decimal("62375.25")


def test_social_security_deduction_below_its_minimum(rules_with_ss: TaxRules) -> None:
    with pytest.raises(ValueError, match="insured salary"):
        social_security_deduction(rules_with_ss, Decimal(749_999))


def test_no_social_security_deduction_without_social_security(rules: TaxRules) -> None:
    assert social_security_deduction(rules, Decimal(1_000_000)) == 0


def test_salary_breakdown(rules_with_ss: TaxRules) -> None:
    breakdown = salary_breakdown(rules_with_ss, Decimal(1_000_000), insured_salary=Decimal(750_000))

    assert breakdown == SalaryBreakdown(
        gross=Decimal(1_000_000),
        social_security=Decimal(52_500),
        taxable=Decimal(947_500),
        tax=Decimal(14_200),
    )
    assert breakdown.net == Decimal(933_300)


@pytest.mark.parametrize(
    "net, expected_gross",
    [
        (Decimal(837_000), Decimal(837_000)),
        (Decimal(1_000_000), Decimal(1_024_100)),
        (Decimal(1_712_500), Decimal(1_860_600)),
        (Decimal(2_000_000), Decimal(2_198_800)),
        # 0.x returned 2,463,200; 2,463,100 gives the same exact net and costs less.
        (Decimal(2_224_700), Decimal(2_463_100)),
        (Decimal(4_350_000), Decimal(4_963_500)),
    ],
)
def test_gross_salary(rules: TaxRules, net: Decimal, expected_gross: Decimal) -> None:
    assert gross_salary(rules, net) == expected_gross


@pytest.mark.parametrize(
    "net, expected_gross",
    [
        (Decimal(837_000), Decimal(837_000)),
        (Decimal(1_000_000), Decimal(1_024_058)),
        (Decimal(1_712_500), Decimal(1_860_506)),
        # 0.x returned one less for the next three, leaving the net up to 0.15 below target.
        (Decimal(2_000_000), Decimal(2_198_742)),
        (Decimal(2_224_700), Decimal(2_463_095)),
        (Decimal(4_350_000), Decimal(4_963_448)),
    ],
)
def test_gross_salary_to_the_cent(
    cent_rules: TaxRules, net: Decimal, expected_gross: Decimal
) -> None:
    assert gross_salary(cent_rules, net) == expected_gross


def test_gross_salary_with_social_security(rules_with_ss: TaxRules) -> None:
    net = Decimal(1_000_000)

    gross = gross_salary(rules_with_ss, net)

    assert salary_breakdown(rules_with_ss, gross).net >= net
    assert salary_breakdown(rules_with_ss, gross - 1).net < net


def test_gross_salary_below_the_minimum_salary(rules: TaxRules) -> None:
    with pytest.raises(SalaryBelowMinimumError):
        gross_salary(rules, rules.min_salary - 1)
