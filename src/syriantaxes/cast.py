from collections.abc import Callable
from decimal import Decimal, InvalidOperation

from .types import Number


def to_decimal(value: Number) -> Decimal:
    """Convert value to Decimal, going through str so a float keeps its printed value."""
    try:
        return Decimal(str(value))
    except InvalidOperation:
        message = f"expected a number, got {value!r}"
        raise TypeError(message) from None


def validated(value: Number, is_valid: Callable[[Decimal], bool], requirement: str) -> Decimal:
    """Convert value to Decimal and raise ValueError unless it meets the requirement."""
    number = to_decimal(value)

    if not is_valid(number):
        message = f"expected {requirement}, got {number}"
        raise ValueError(message)

    return number


def to_non_negative(value: Number) -> Decimal:
    return validated(value, lambda number: number >= 0, "a number >= 0")


def to_positive(value: Number) -> Decimal:
    return validated(value, lambda number: number > 0, "a number > 0")


def to_rate(value: Number) -> Decimal:
    return validated(value, lambda number: 0 <= number <= 1, "a rate between 0 and 1")
