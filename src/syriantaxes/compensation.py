from decimal import Decimal

from .rules import TaxRules


def compensation_tax(rules: TaxRules, amount: Decimal) -> Decimal:
    """Flat tax on a compensation amount."""
    return rules.rounding(amount * rules.compensation_tax_rate)


def gross_compensation(rules: TaxRules, net: Decimal) -> Decimal:
    """Return the compensation that leaves net after the flat compensation tax."""
    return rules.rounding(net / (1 - rules.compensation_tax_rate))
