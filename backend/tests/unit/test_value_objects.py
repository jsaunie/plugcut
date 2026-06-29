"""Unit tests for shared value objects."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.shared.value_objects import (
    CurrencyMismatch,
    Money,
    NegativeMoney,
    Percentage,
    PercentageOutOfRange,
)


class TestMoney:
    def test_rounds_to_cents(self) -> None:
        assert Money(Decimal("10.005")).amount == Decimal("10.01")

    def test_rejects_negative(self) -> None:
        with pytest.raises(NegativeMoney):
            Money(Decimal("-1"))

    def test_addition_requires_same_currency(self) -> None:
        with pytest.raises(CurrencyMismatch):
            Money(Decimal("1"), "EUR") + Money(Decimal("1"), "USD")

    def test_multiplication_scales_amount(self) -> None:
        assert Money(Decimal("100")) * 3 == Money(Decimal("300"))

    def test_equality_is_by_value(self) -> None:
        assert Money(Decimal("5"), "eur") == Money(Decimal("5"), "EUR")


class TestPercentage:
    def test_rate_is_fraction(self) -> None:
        assert Percentage(Decimal("10")).rate == Decimal("0.10")

    def test_of_money(self) -> None:
        assert Percentage(Decimal("10")).of(Money(Decimal("500"))) == Money(Decimal("50"))

    @pytest.mark.parametrize("value", [Decimal("-1"), Decimal("101")])
    def test_rejects_out_of_range(self, value: Decimal) -> None:
        with pytest.raises(PercentageOutOfRange):
            Percentage(value)
