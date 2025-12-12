import decimal
from typing import Protocol, TypeAlias

Number: TypeAlias = int | float | decimal.Decimal | str


class Rounder(Protocol):
    def round(self, number: Number) -> decimal.Decimal: ...
