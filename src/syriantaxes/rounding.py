from collections.abc import Callable
from decimal import ROUND_HALF_EVEN, Decimal
from typing import TypeAlias

Rounding: TypeAlias = Callable[[Decimal], Decimal]


def round_to(step: Decimal, method: str = ROUND_HALF_EVEN) -> Rounding:
    """Make a rounding function to the nearest multiple of step.

    method is one of the decimal module's rounding modes, such as decimal.ROUND_CEILING.
    """
    if step <= 0:
        message = f"step must be > 0, got {step}"
        raise ValueError(message)

    def rounding(amount: Decimal) -> Decimal:
        return (amount / step).to_integral_value(method) * step

    return rounding


to_cents = round_to(Decimal("0.01"))
