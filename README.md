# Syriantaxes

A Python package for calculating taxes and compensations for Syrian salaries based on Syrian tax laws.

## Features

- Calculate fixed taxes and bracket-based taxes
- Handle social security deductions
- Support for custom rounding methods
- Protocol-based design for extensibility
- 100% test coverage with 178 successful test cases

## Installation

Install Syriantaxes using pip:

```bash
pip install syriantaxes
```

Or using uv:

```bash
uv add syriantaxes
```

## Quick Start

```python
from decimal import Decimal
from syriantaxes import Bracket, Rounder, RoundingMethod, SocialSecurity, calculate_brackets_tax

# Define tax brackets
brackets = [
    Bracket(0, 837_000, 0),
    Bracket(837_000, 850_000, Decimal("0.11")),
    Bracket(850_000, 1_100_000, Decimal("0.13")),
    Bracket(1_100_000, 25_000_000, Decimal("0.15")),
]

# Create a rounder
rounder = Rounder(RoundingMethod.CEILING, 100)

# Create social security object
ss = SocialSecurity(Decimal(750_000), Decimal("0.07"), rounder)

# Calculate tax
salary = Decimal(1_000_000)
tax = calculate_brackets_tax(salary, brackets, Decimal(837_000), rounder, ss)
print(f"Tax: {tax}")  # Tax: 11900
```

## Classes

### Bracket

Represents a tax bracket with minimum, maximum, and rate.

```python
from syriantaxes import Bracket
from decimal import Decimal

bracket = Bracket(0, 837_000, 0)
print(bracket.min)  # 0
print(bracket.max)  # 837000
print(bracket.rate)  # 0
```

`Bracket`, `Rounder` and `SocialSecurity` are immutable: their values are checked when they are created and can't be changed afterwards. To change a value, create a new object.

### Rounder

Handles rounding of decimal numbers using various methods.

```python
from syriantaxes import Rounder, RoundingMethod

rounder = Rounder(RoundingMethod.CEILING, 100)
result = rounder.round(Decimal("123.45"))
print(result)  # 200
```

Available rounding methods:

- `ROUND_DOWN`
- `ROUND_HALF_UP`
- `ROUND_HALF_EVEN`
- `ROUND_CEILING`
- `ROUND_FLOOR`
- `ROUND_UP`
- `ROUND_HALF_DOWN`
- `ROUND_05UP`

### SocialSecurity

Calculates social security deductions.

```python
from syriantaxes import SocialSecurity, Rounder, RoundingMethod

rounder = Rounder(RoundingMethod.CEILING, 1)
ss = SocialSecurity(Decimal(750_000), Decimal("0.07"), rounder)
deduction = ss.calculate_deduction(Decimal(1_000_000))
print(deduction)  # 70000
```

## Functions

### calculate_fixed_tax

Calculate fixed tax for an amount.

```python
from syriantaxes import calculate_fixed_tax, Rounder, RoundingMethod

rounder = Rounder(RoundingMethod.CEILING, 100)
tax = calculate_fixed_tax(Decimal(1_000_000), Decimal("0.05"), rounder)
print(tax)  # 50000
```

### calculate_brackets_tax

Calculate tax based on progressive brackets.

```python
from syriantaxes import calculate_brackets_tax, Bracket, SocialSecurity, Rounder, RoundingMethod

brackets = [
    Bracket(0, 837_000, 0),
    Bracket(837_000, 850_000, Decimal("0.11")),
    Bracket(850_000, 1_100_000, Decimal("0.13")),
]

rounder = Rounder(RoundingMethod.CEILING, 100)
ss = SocialSecurity(Decimal(750_000), Decimal("0.07"), rounder)

tax = calculate_brackets_tax(Decimal(1_000_000), brackets, Decimal(837_000), rounder, ss)
print(tax)  # 11900
```

### calculate_gross_compensation

Calculate gross compensation from net amount.

```python
from syriantaxes import calculate_gross_compensation

gross = calculate_gross_compensation(Decimal(1_000_000), Decimal("0.05"))
print(gross)  # 1052631.58
```

### calculate_gross_salary

Calculate gross salary from net target.

```python
from syriantaxes import calculate_gross_salary, Bracket

brackets = [
    Bracket(0, 837_000, 0),
    Bracket(837_000, 850_000, Decimal("0.11")),
    Bracket(850_000, 1_100_000, Decimal("0.13")),
]

gross = calculate_gross_salary(Decimal(1_000_000), brackets, Decimal(837_000))
print(gross)  # 1024058
```

### calculate_gross_components

Calculate gross salary and compensations.

```python
from syriantaxes import calculate_gross_components, Bracket

brackets = [
    Bracket(0, 837_000, 0),
    Bracket(837_000, 850_000, Decimal("0.11")),
    Bracket(850_000, 1_100_000, Decimal("0.13")),
]

salary, compensations = calculate_gross_components(
    Decimal(1_000_000), Decimal("0.2"), brackets, Decimal(837_000), Decimal("0.05")
)
print(f"Salary: {salary}, Compensations: {compensations}")
```

`rounder` must be passed by keyword here (`rounder=...`), as must `ss_salary` in `calculate_brackets_tax`.

### Errors

`calculate_gross_salary` and `calculate_gross_components` raise `SalaryBelowMinimumError` (a `ValueError` subclass) when the target is below `min_allowed_salary`.

```python
from syriantaxes import SalaryBelowMinimumError, calculate_gross_salary

try:
    calculate_gross_salary(Decimal(500_000), brackets, Decimal(837_000))
except SalaryBelowMinimumError as error:
    print(error)  # Can't be calculated for salary less than 837000.
```

`calculate_gross_salary` raises `NoExactGrossSalaryError` (also a `ValueError`) when no whole-number gross salary gives exactly the target net, for example when a 100% bracket caps the net.

## Advanced Examples with External Classes

Syriantaxes uses protocols, allowing you to implement custom classes that conform to the expected interfaces.

### Custom SocialSecurity

```python
from decimal import Decimal
from math import ceil
from syriantaxes import calculate_brackets_tax


class CustomSocialSecurity:
    def __init__(self, min_salary: Decimal):
        self._min_salary = min_salary

    def calculate_deduction(self, salary: Decimal) -> Decimal:
        deduction = Decimal(salary) * Decimal("0.07")
        return Decimal(ceil(deduction))


# Custom brackets as dicts
brackets = [
    {"min": 0, "max": 837_000, "rate": 0},
    {"min": 837_000, "max": 850_000, "rate": 0.11},
    {"min": 850_000, "max": 1_100_000, "rate": 0.13},
]

ss = CustomSocialSecurity(Decimal(750_000))

tax = calculate_brackets_tax(Decimal(1_000_000), brackets, Decimal(500_000), ss_obj=ss)
print(tax)  # 20930
```

### Custom Rounder

```python
from decimal import Decimal
from math import ceil
from syriantaxes import calculate_fixed_tax


class CustomRounder:
    def round(self, number: Decimal) -> Decimal:
        return Decimal(ceil(number / 100) * 100)


rounder = CustomRounder()
tax = calculate_fixed_tax(Decimal(1_000_000), Decimal("0.05"), rounder)
print(tax)  # 50000
```

### Custom Brackets

You can use classes with properties, variables, or class variables:

```python
from syriantaxes import calculate_brackets_tax


class CustomBracket:
    def __init__(self, min_val, max_val, rate_val):
        self.min = min_val
        self.max = max_val
        self.rate = rate_val


brackets = [
    CustomBracket(0, 837_000, 0),
    CustomBracket(837_000, 850_000, 0.11),
    CustomBracket(850_000, 1_100_000, 0.13),
]

tax = calculate_brackets_tax(Decimal(1_000_000), brackets, Decimal(500_000))
print(tax)  # 20930
```

## Testing

The package has comprehensive test coverage:

- **Coverage**: 100%
- **Test Cases**: 178 successful tests

The project uses [uv](https://docs.astral.sh/uv/). Set up the environment with:

```bash
uv sync
```

Run the tests with coverage:

```bash
uv run pytest --cov
```

Type-check with mypy (strict mode):

```bash
uv run mypy
```

Lint and check formatting with ruff:

```bash
uv run ruff check
```

```bash
uv run ruff format --check
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Abdullah Altatan - <a.altatan@gmail.com>
