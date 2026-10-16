from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

from .compensation import gross_compensation
from .rules import TaxRules
from .salary import SalaryBelowMinimumError, gross_salary, salary_breakdown


@dataclass(frozen=True)
class Package:
    salary: Decimal
    compensation: Decimal


def split_net_package(rules: TaxRules, net_total: Decimal, compensation_share: Decimal) -> Package:
    """Split a wanted net total into a gross salary and a gross compensation.

    compensation_share of the net total is paid as compensation and the rest as salary. If the
    salary part would fall below the minimum salary, the salary is the minimum and the
    compensation makes up the difference.
    """
    if not 0 <= compensation_share <= 1:
        message = f"compensation_share must be between 0 and 1, got {compensation_share}"
        raise ValueError(message)

    if net_total < rules.min_salary:
        raise SalaryBelowMinimumError(rules.min_salary)

    net_salary = (net_total * (1 - compensation_share)).to_integral_value(ROUND_DOWN)

    if net_salary < rules.min_salary:
        salary = rules.min_salary
        net_compensation = net_total - salary_breakdown(rules, salary).net
    else:
        salary = gross_salary(rules, net_salary)
        net_compensation = net_total - net_salary

    return Package(salary, gross_compensation(rules, net_compensation))
