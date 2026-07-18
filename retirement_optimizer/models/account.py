from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Account:
    name: str
    balance: float
    expected_return: float = 0.05
    cost_basis: float = 0.0
    rollover_eligible: bool = False
    early_access_protected: bool = False

    def grow(self, annual_return: float | None = None) -> None:
        rate = self.expected_return if annual_return is None else annual_return
        self.balance = max(0.0, self.balance * (1.0 + rate))

    def withdraw(self, amount: float) -> float:
        taken = min(max(amount, 0.0), self.balance)
        self.balance -= taken
        return taken

    def deposit(self, amount: float) -> None:
        self.balance += max(amount, 0.0)
