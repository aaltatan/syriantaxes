import decimal
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from .cast import to_decimal, to_positive
from .types import Number
from .types import Rounder as RounderProtocol


class RoundingMethod(str, Enum):
    DOWN = decimal.ROUND_DOWN
    HALF_UP = decimal.ROUND_HALF_UP
    HALF_EVEN = decimal.ROUND_HALF_EVEN
    CEILING = decimal.ROUND_CEILING
    FLOOR = decimal.ROUND_FLOOR
    UP = decimal.ROUND_UP
    HALF_DOWN = decimal.ROUND_HALF_DOWN
    UP05 = decimal.ROUND_05UP


@dataclass(frozen=True, init=False)
class Rounder:
    method: RoundingMethod
    to_nearest: Decimal

    def __init__(self, method: RoundingMethod, to_nearest: Number) -> None:
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "to_nearest", to_positive(to_nearest))

    def round(self, number: Number) -> Decimal:
        steps = to_decimal(number) / self.to_nearest
        return steps.to_integral_value(self.method) * self.to_nearest


TO_CENTS = Rounder(RoundingMethod.HALF_EVEN, "0.01")


def apply_rounding(value: Decimal, rounder: RounderProtocol | None) -> Decimal:
    """Round value with rounder, or return it unchanged when there is no rounder."""
    return value if rounder is None else rounder.round(value)
