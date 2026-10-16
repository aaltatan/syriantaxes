from collections.abc import Iterable
from decimal import Decimal
from typing import ClassVar, Protocol, TypeAlias, TypedDict

Number: TypeAlias = int | float | Decimal | str


class Rounder(Protocol):
    def round(self, number: Number) -> Decimal: ...


class DeductionCalculator(Protocol):
    def calculate_deduction(self, salary: Number) -> Decimal: ...


class BracketLike(Protocol):
    """Any object exposing min, max and rate, as plain attributes or properties."""

    @property
    def min(self) -> Number: ...

    @property
    def max(self) -> Number: ...

    @property
    def rate(self) -> Number: ...


class BracketWithClassVars(Protocol):
    min: ClassVar[Number]
    max: ClassVar[Number]
    rate: ClassVar[Number]


class BracketDict(TypedDict):
    min: Number
    max: Number
    rate: Number


AnyBracket: TypeAlias = BracketLike | BracketWithClassVars | BracketDict
Brackets: TypeAlias = Iterable[AnyBracket]
