from decimal import Decimal

from .cast import cast_to_decimal
from .types import Number


class Bracket:
    def __init__(self, _min: Number, _max: Number, rate: Number) -> None:
        self._min = cast_to_decimal(_min, lt=0)
        self._max = cast_to_decimal(_max, lte=self._min)
        self._rate = cast_to_decimal(rate, lt=0, gt=1)

    @property
    def min(self) -> Decimal:
        return self._min

    @min.setter
    def min(self, value: Number) -> None:
        self._min = cast_to_decimal(value, lt=0, gte=self._max)

    @property
    def max(self) -> Decimal:
        return self._max

    @max.setter
    def max(self, value: Number) -> None:
        self._max = cast_to_decimal(value, lte=self._min)

    @property
    def rate(self) -> Decimal:
        return self._rate

    @rate.setter
    def rate(self, value: Number) -> None:
        self._rate = cast_to_decimal(value, lt=0, gt=1)

    def __repr__(self) -> str:
        return f"Bracket(min={self._min}, max={self._max}, rate={self._rate})"
