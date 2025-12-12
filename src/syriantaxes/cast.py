from decimal import Decimal, InvalidOperation

from .types import Number


def _cast_to_decimal(value: Number) -> Decimal:
    if isinstance(value, Decimal):
        return value

    try:
        result = Decimal(value if isinstance(value, str) else str(value))
    except InvalidOperation:
        message = "value must be a number (float or Decimal)"
        raise TypeError(message) from None

    return result


def cast_to_decimal(
    value: Number,
    lt: Number | None = None,
    gt: Number | None = None,
    lte: Number | None = None,
    gte: Number | None = None,
) -> Decimal:
    result = _cast_to_decimal(value)

    if lt is not None:
        lt = _cast_to_decimal(lt)
        if result < lt:
            message = f"value must be greater than {lt}"
            raise ValueError(message)

    if gt is not None:
        gt = _cast_to_decimal(gt)
        if result > gt:
            message = f"value must be less than {gt}"
            raise ValueError(message)

    if lte is not None:
        lte = _cast_to_decimal(lte)
        if result <= lte:
            message = f"value must be greater than or equal to {lte}"
            raise ValueError(message)

    if gte is not None:
        gte = _cast_to_decimal(gte)
        if result >= gte:
            message = f"value must be less than or equal to {gte}"
            raise ValueError(message)

    return result
