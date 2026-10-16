from decimal import Decimal

import pytest

from syriantaxes import TaxRules, compensation_tax, gross_compensation


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (Decimal(1_000_000), Decimal(50_000)),
        (Decimal(2_000_000), Decimal(100_000)),
        (Decimal(155_770), Decimal(7_800)),
        (Decimal(221_300), Decimal(11_100)),
    ],
)
def test_compensation_tax(rules: TaxRules, amount: Decimal, expected_tax: Decimal) -> None:
    assert compensation_tax(rules, amount) == expected_tax


@pytest.mark.parametrize(
    "amount, expected_tax",
    [
        (Decimal(1_000_000), Decimal(50_000)),
        (Decimal(2_000_000), Decimal(100_000)),
        (Decimal(155_770), Decimal("7788.5")),
        (Decimal(221_350), Decimal("11067.5")),
    ],
)
def test_compensation_tax_to_the_cent(
    cent_rules: TaxRules, amount: Decimal, expected_tax: Decimal
) -> None:
    assert compensation_tax(cent_rules, amount) == expected_tax


@pytest.mark.parametrize(
    "net, expected_gross",
    [
        (Decimal(1_000_000), Decimal(1_052_700)),
        (Decimal(2_000_000), Decimal(2_105_300)),
        (Decimal(-2_000_000), Decimal(-2_105_200)),
    ],
)
def test_gross_compensation(rules: TaxRules, net: Decimal, expected_gross: Decimal) -> None:
    assert gross_compensation(rules, net) == expected_gross


@pytest.mark.parametrize(
    "net, expected_gross",
    [
        (Decimal(650_300), Decimal("684526.32")),
        (Decimal(277_550), Decimal("292157.89")),
        (Decimal(241_241), Decimal("253937.89")),
        (Decimal(-241_241), Decimal("-253937.89")),
    ],
)
def test_gross_compensation_to_the_cent(
    cent_rules: TaxRules, net: Decimal, expected_gross: Decimal
) -> None:
    assert gross_compensation(cent_rules, net) == expected_gross
