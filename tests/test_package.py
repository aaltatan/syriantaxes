from decimal import Decimal

import pytest

from syriantaxes import Package, SalaryBelowMinimumError, TaxRules, split_net_package


@pytest.mark.parametrize(
    "net_total, expected",
    [
        (Decimal(850_000), Package(Decimal(837_000), Decimal(13_700))),
        (Decimal(3_450_000), Package(Decimal(866_100), Decimal(2_723_700))),
        (Decimal(4_000_000), Package(Decimal(1_024_100), Decimal(3_157_900))),
        (Decimal(4_150_000), Package(Decimal(1_067_200), Decimal(3_276_400))),
        (Decimal(5_150_000), Package(Decimal(1_360_600), Decimal(4_065_800))),
    ],
)
def test_split_net_package(rules: TaxRules, net_total: Decimal, expected: Package) -> None:
    assert split_net_package(rules, net_total, Decimal("0.75")) == expected


def test_split_net_package_below_the_minimum_salary(rules: TaxRules) -> None:
    with pytest.raises(SalaryBelowMinimumError):
        split_net_package(rules, rules.min_salary - 1, Decimal("0.75"))


@pytest.mark.parametrize("share", [Decimal("-0.1"), Decimal("1.1")])
def test_split_net_package_rejects_an_invalid_share(rules: TaxRules, share: Decimal) -> None:
    with pytest.raises(ValueError, match="compensation_share"):
        split_net_package(rules, Decimal(1_000_000), share)
