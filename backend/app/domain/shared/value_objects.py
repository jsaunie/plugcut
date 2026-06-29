"""Shared, framework-free value objects.

Value objects are immutable and compared by value. They enforce their own invariants at
construction time, so an instance can never exist in an invalid state.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.shared.errors import InvariantViolation

_CENTS = Decimal("0.01")


class CurrencyMismatch(InvariantViolation):
    code = "money.currency_mismatch"


class NegativeMoney(InvariantViolation):
    code = "money.negative"


@dataclass(frozen=True, slots=True)
class Money:
    """A non-negative monetary amount in a single currency.

    Amounts are stored as :class:`~decimal.Decimal` rounded to cents to avoid the
    floating-point errors that are unacceptable in a billing domain.
    """

    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount < 0:
            raise NegativeMoney
        object.__setattr__(self, "amount", self.amount.quantize(_CENTS, ROUND_HALF_UP))
        object.__setattr__(self, "currency", self.currency.upper())

    @classmethod
    def zero(cls, currency: str = "EUR") -> Money:
        return cls(Decimal("0"), currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatch

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Decimal | int) -> Money:
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


class PercentageOutOfRange(InvariantViolation):
    code = "percentage.out_of_range"


@dataclass(frozen=True, slots=True)
class Percentage:
    """A percentage in the inclusive range [0, 100]."""

    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, "value", Decimal(str(self.value)))
        if not (Decimal("0") <= self.value <= Decimal("100")):
            raise PercentageOutOfRange

    @property
    def rate(self) -> Decimal:
        """The fractional rate, e.g. ``10`` percent -> ``Decimal('0.10')``."""
        return self.value / Decimal("100")

    def of(self, money: Money) -> Money:
        return money * self.rate

    def __str__(self) -> str:
        return f"{self.value}%"
