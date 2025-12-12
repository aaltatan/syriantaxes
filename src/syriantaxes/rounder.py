from decimal import Decimal
from enum import Enum

from .cast import cast_to_decimal
from .types import Number


class RoundingMethod(str, Enum):
    DOWN = "ROUND_DOWN"
    HALF_UP = "ROUND_HALF_UP"
    HALF_EVEN = "ROUND_HALF_EVEN"
    CEILING = "ROUND_CEILING"
    FLOOR = "ROUND_FLOOR"
    UP = "ROUND_UP"
    HALF_DOWN = "ROUND_HALF_DOWN"
    UP05 = "ROUND_05UP"


class Rounder:
    def __init__(self, method: RoundingMethod, to_nearest: Number) -> None:
        self._method = method
        self._to_nearest = cast_to_decimal(to_nearest, lt=0)

    def round(self, number: Number) -> Decimal:
        value = cast_to_decimal(number)

        return (value / self._to_nearest).to_integral_value(
            self._method
        ) * self._to_nearest

    @property
    def to_nearest(self) -> Decimal:
        return self._to_nearest

    @to_nearest.setter
    def to_nearest(self, value: Number) -> None:
        self._to_nearest = cast_to_decimal(value, lt=0)
