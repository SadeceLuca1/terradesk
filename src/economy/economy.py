"""
TerraDesk – Economy System
Manages village budget, taxes, trade, and resources.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from src.core.constants import (
    STARTING_MONEY, TAX_RATE_DEFAULT, CITIZEN_SALARY,
    FOOD_PRICE, WOOD_PRICE, STONE_PRICE
)

if TYPE_CHECKING:
    from src.core.game import Game


class Economy:
    def __init__(self):
        self.money: float = STARTING_MONEY
        self.tax_rate: float = TAX_RATE_DEFAULT
        self.day_income: float = 0.0
        self.day_expenses: float = 0.0

        # Resources
        self.food: float = 200.0
        self.wood: float = 150.0
        self.stone: float = 100.0

        # Trade (simple market)
        self.food_price: float = FOOD_PRICE
        self.wood_price: float = WOOD_PRICE
        self.stone_price: float = STONE_PRICE

        # Statistics
        self.total_earned: float = 0.0
        self.total_spent: float = 0.0
        self._tick_timer: int = 0
        self._daily_income_log: list = []
        self._daily_expense_log: list = []

    # ------------------------------------------------------------------ update

    def update(self, game: "Game"):
        """Called every sim tick."""
        self._tick_timer += 1

        # Collect taxes once per sim-day (every HOURS_PER_DAY * ticks)
        # Also update food consumption
        if self._tick_timer % 100 == 0:
            self._produce_resources(game)
            self._consume_resources(game)
            self._pay_salaries(game)

        # Daily tax collection at midnight
        if game.time_manager.hour == 0 and game.time_manager.minute == 0 and self._tick_timer % 10 == 0:
            self._collect_taxes(game)
            self._pay_building_upkeep(game)
            self._log_daily()

    def _collect_taxes(self, game):
        pop = game.citizen_manager.count
        tax = pop * CITIZEN_SALARY * self.tax_rate
        self.money += tax
        self.day_income += tax
        self.total_earned += tax

    def _pay_salaries(self, game):
        for cit in game.citizen_manager.all_citizens():
            if cit.workplace_id:
                salary_tick = cit.salary / (24 * 60 * 10)  # per 100 ticks
                cost = min(salary_tick, self.money)
                self.money -= cost
                cit.money += cost
                self.day_expenses += cost
                self.total_spent += cost

    def _pay_building_upkeep(self, game):
        for bld in game.building_manager.all_buildings():
            cost = bld.daily_upkeep
            self.money -= cost
            self.day_expenses += cost
            self.total_spent += cost

    def _produce_resources(self, game):
        bm = game.building_manager
        prod_rate = 0.05  # per 100 ticks
        food_prod = bm.total_food_production() * prod_rate
        self.food = min(5000, self.food + food_prod)

        # Wood from forests (background)
        self.wood = min(2000, self.wood + 0.3)
        self.stone = min(1500, self.stone + 0.1)

    def _consume_resources(self, game):
        pop = game.citizen_manager.count
        self.food = max(0, self.food - pop * 0.02)

    def _log_daily(self):
        self._daily_income_log.append(self.day_income)
        self._daily_expense_log.append(self.day_expenses)
        if len(self._daily_income_log) > 30:
            self._daily_income_log.pop(0)
        if len(self._daily_expense_log) > 30:
            self._daily_expense_log.pop(0)
        self.day_income = 0.0
        self.day_expenses = 0.0

    # ------------------------------------------------------------------ transactions

    def can_afford(self, amount: float) -> bool:
        return self.money >= amount

    def spend(self, amount: float) -> bool:
        if self.can_afford(amount):
            self.money -= amount
            self.total_spent += amount
            self.day_expenses += amount
            return True
        return False

    def add_money(self, amount: float):
        self.money += amount
        self.total_earned += amount
        self.day_income += amount

    def set_money(self, amount: float):
        self.money = max(0, amount)

    # ------------------------------------------------------------------ resource trade

    def buy_resource(self, resource: str, amount: float) -> bool:
        prices = {"food": self.food_price, "wood": self.wood_price, "stone": self.stone_price}
        price = prices.get(resource, 10)
        cost = amount * price
        if self.spend(cost):
            setattr(self, resource, getattr(self, resource, 0) + amount)
            return True
        return False

    def sell_resource(self, resource: str, amount: float) -> bool:
        current = getattr(self, resource, 0)
        actual = min(amount, current)
        if actual <= 0:
            return False
        setattr(self, resource, current - actual)
        prices = {"food": self.food_price, "wood": self.wood_price, "stone": self.stone_price}
        self.add_money(actual * prices.get(resource, 10) * 0.8)  # sell at 80%
        return True

    # ------------------------------------------------------------------ stats

    @property
    def balance(self):
        return self.day_income - self.day_expenses

    @property
    def average_daily_income(self):
        if not self._daily_income_log:
            return 0
        return sum(self._daily_income_log) / len(self._daily_income_log)

    @property
    def average_daily_expense(self):
        if not self._daily_expense_log:
            return 0
        return sum(self._daily_expense_log) / len(self._daily_expense_log)

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            "money": self.money,
            "tax_rate": self.tax_rate,
            "food": self.food,
            "wood": self.wood,
            "stone": self.stone,
            "total_earned": self.total_earned,
            "total_spent": self.total_spent,
        }

    @classmethod
    def from_dict(cls, d):
        e = cls()
        e.money = d.get("money", STARTING_MONEY)
        e.tax_rate = d.get("tax_rate", TAX_RATE_DEFAULT)
        e.food = d.get("food", 200)
        e.wood = d.get("wood", 150)
        e.stone = d.get("stone", 100)
        e.total_earned = d.get("total_earned", 0)
        e.total_spent = d.get("total_spent", 0)
        return e