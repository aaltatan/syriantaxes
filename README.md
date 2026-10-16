# Syriantaxes

A Python package for calculating taxes and compensations for Syrian salaries based on Syrian tax laws.

- Progressive salary tax, with social security deducted first
- Flat tax on compensations
- The reverse problems: the gross salary or compensation that gives a wanted net
- Splitting a net package into salary and compensation
- `Decimal` in, `Decimal` out; fully typed (mypy strict), with 100% test coverage

## Installation

```bash
pip install syriantaxes
```

Or using uv:

```bash
uv add syriantaxes
```

## The idea

Everything the law fixes for a period (the brackets, rates, minimum salary and rounding) goes into
one immutable `TaxRules` value. Every calculation is a plain function of those rules and an amount.
When the law changes, you make new rules; your code stays the same.

```python
from decimal import ROUND_CEILING, Decimal

from syriantaxes import Bracket, SocialSecurity, TaxRules, round_to

rules = TaxRules(
    brackets=(
        Bracket(lower=Decimal(0), rate=Decimal(0)),
        Bracket(lower=Decimal(837_000), rate=Decimal("0.11")),
        Bracket(lower=Decimal(850_000), rate=Decimal("0.13")),
        Bracket(lower=Decimal(1_100_000), rate=Decimal("0.15")),
    ),
    min_salary=Decimal(837_000),
    compensation_tax_rate=Decimal("0.05"),
    social_security=SocialSecurity(
        rate=Decimal("0.07"),
        min_salary=Decimal(750_000),
        rounding=round_to(Decimal(1), ROUND_CEILING),
    ),
    rounding=round_to(Decimal(100), ROUND_CEILING),  # taxes are rounded up to 100
)
```

The rules are checked when they are created:
- the brackets must start at 0 and go up;
- every rate must be at least 0 and below 1;
- amounts can't be negative.

## Salary

Each bracket runs from its `lower` up to the next bracket's `lower`; the last one has no top.

```python
from syriantaxes import gross_salary, salary_breakdown, salary_tax

breakdown = salary_breakdown(rules, Decimal(1_000_000), insured_salary=Decimal(750_000))
print(breakdown.social_security, breakdown.taxable, breakdown.tax, breakdown.net)
# 52500 947500 14200 933300

print(salary_tax(rules, Decimal(1_000_000)))  # 11900

print(gross_salary(rules, Decimal(1_000_000)))  # 1101183
```

- `insured_salary` is the salary that social security is based on; it defaults to the gross salary.
- `gross_salary` returns the first whole gross salary whose net (after social security and tax) is at least the target. It solves the brackets exactly and then accounts for rounding, so there is no search range to tune.

## Compensation

```python
from syriantaxes import compensation_tax, gross_compensation

print(compensation_tax(rules, Decimal(1_000_000)))  # 50000
print(gross_compensation(rules, Decimal(1_000_000)))  # 1052700
```

## Splitting a net package

`split_net_package` pays `compensation_share` of a net total as compensation and the rest as salary.
If the salary part would be below the minimum salary, the salary is set to the minimum and the
compensation makes up the difference.

```python
from syriantaxes import split_net_package

package = split_net_package(rules, Decimal(4_000_000), Decimal("0.75"))
print(package.salary, package.compensation)  # 1101183 3157900
```

## Rounding

A rounding rule is any function from `Decimal` to `Decimal`. `round_to(step, method)` makes one that
rounds to a multiple of `step`, using any of the `decimal` module's rounding modes. Without a
rounding rule, amounts are rounded half-even to the cent (`to_cents`).

## Inputs: Decimal only

Syriantaxes doesn't convert inputs: turn ints, floats or strings into `Decimal` yourself. Build
decimals from strings or ints, never from floats: `Decimal("0.11")` is exactly 0.11, while
`Decimal(0.11)` isn't.

## Errors

- `SalaryBelowMinimumError` (a `ValueError`): `gross_salary` and `split_net_package` raise it when the target is below `rules.min_salary`.
- `ValueError`: raised for invalid rules or arguments, such as a rate of 1, or an insured salary below the social security minimum.

## Upgrading from 0.x

1.0 is a new API. The old functions map like this:

| 0.x | 1.0 |
| --- | --- |
| `calculate_brackets_tax(amount, brackets, min_allowed_salary, rounder, ss_obj, ss_salary=...)` | `salary_tax(rules, gross, insured_salary=...)` |
| `calculate_fixed_tax(amount, rate, rounder)` | `compensation_tax(rules, amount)` |
| `calculate_gross_compensation(target, rate, rounder)` | `gross_compensation(rules, net)` |
| `calculate_gross_salary(target, brackets, min_allowed_salary, rounder)` | `gross_salary(rules, net)` |
| `calculate_gross_components(target, rate, brackets, min_allowed_salary, tax_rate, rounder=...)` | `split_net_package(rules, net_total, compensation_share)` |
| `Bracket(min, max, rate)` | `Bracket(lower, rate)` |
| `Rounder(RoundingMethod.CEILING, 100)` | `round_to(Decimal(100), ROUND_CEILING)` |

Behavior changes:
- `gross_salary` never returns a gross whose net is below the target. Where tax is rounded to the cent, 0.x could return a gross 1 lower, whose net fell up to 0.15 short of the target.
- When more than one gross gives the exact target net, `gross_salary` returns the smallest.
- Custom social security objects are replaced by `SocialSecurity` rules. Custom rounders are plain functions.

## Development

The project uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

```bash
uv run pytest --cov
```

```bash
uv run mypy
```

```bash
uv run ruff check
```

```bash
uv run ruff format --check
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Abdullah Altatan - <a.altatan@gmail.com>
