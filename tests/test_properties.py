from decimal import ROUND_CEILING, Decimal

from hypothesis import given
from hypothesis import strategies as st

from syriantaxes import (
    TaxRules,
    compensation_tax,
    gross_compensation,
    gross_salary,
    round_to,
    salary_breakdown,
)

from .conftest import BRACKETS, SOCIAL_SECURITY

CENT_RULES = TaxRules(
    brackets=BRACKETS,
    min_salary=Decimal(837_000),
    compensation_tax_rate=Decimal("0.05"),
)
HUNDREDS_RULES = TaxRules(
    brackets=BRACKETS,
    min_salary=Decimal(837_000),
    compensation_tax_rate=Decimal("0.05"),
    social_security=SOCIAL_SECURITY,
    rounding=round_to(Decimal(100), ROUND_CEILING),
)

salaries = st.decimals(min_value=837_000, max_value=50_000_000, places=0)
amounts = st.decimals(min_value=0, max_value=50_000_000, places=2)


@given(net=salaries)
def test_gross_salary_is_the_smallest_whole_gross_reaching_the_net(net: Decimal) -> None:
    gross = gross_salary(CENT_RULES, net)

    assert salary_breakdown(CENT_RULES, gross).net >= net
    assert salary_breakdown(CENT_RULES, gross - 1).net < net


@given(net=salaries)
def test_gross_salary_reaches_the_net_with_rounding_and_social_security(net: Decimal) -> None:
    gross = gross_salary(HUNDREDS_RULES, net)

    assert salary_breakdown(HUNDREDS_RULES, gross).net >= net


@given(gross=salaries, raise_=st.decimals(min_value=1, max_value=1_000_000, places=0))
def test_tax_never_falls_when_gross_rises(gross: Decimal, raise_: Decimal) -> None:
    lower = salary_breakdown(HUNDREDS_RULES, gross).tax
    higher = salary_breakdown(HUNDREDS_RULES, gross + raise_).tax

    assert higher >= lower


@given(gross=salaries)
def test_tax_is_between_zero_and_the_taxable_salary(gross: Decimal) -> None:
    breakdown = salary_breakdown(CENT_RULES, gross)

    assert 0 <= breakdown.tax <= breakdown.taxable


@given(net=amounts)
def test_gross_compensation_leaves_the_net_after_tax(net: Decimal) -> None:
    gross = gross_compensation(CENT_RULES, net)

    assert abs(gross - compensation_tax(CENT_RULES, gross) - net) <= Decimal("0.01")
