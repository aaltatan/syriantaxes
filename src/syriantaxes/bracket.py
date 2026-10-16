from dataclasses import dataclass
from decimal import Decimal

from .cast import to_non_negative, to_rate, validated
from .types import AnyBracket, Number


@dataclass(frozen=True, init=False)
class Bracket:
    min: Decimal
    max: Decimal
    rate: Decimal

    def __init__(self, min_: Number, max_: Number, rate: Number) -> None:
        lower = to_non_negative(min_)
        upper = validated(max_, lambda number: number > lower, f"a max above {lower}")

        object.__setattr__(self, "min", lower)
        object.__setattr__(self, "max", upper)
        object.__setattr__(self, "rate", to_rate(rate))


def to_bracket(bracket: AnyBracket) -> Bracket:
    """Turn any supported bracket shape (Bracket, dict or object) into a Bracket."""
    if isinstance(bracket, Bracket):
        return bracket

    if isinstance(bracket, dict):
        return Bracket(bracket["min"], bracket["max"], bracket["rate"])

    return Bracket(bracket.min, bracket.max, bracket.rate)


def bracket_tax(bracket: Bracket, salary: Decimal) -> Decimal:
    """Tax on the part of salary that falls inside the bracket."""
    width = bracket.max - bracket.min
    taxed_part = min(max(salary - bracket.min, Decimal(0)), width)
    return taxed_part * bracket.rate
