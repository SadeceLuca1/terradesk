"""
TerraDesk – Building Manager
Handles placement, removal, lookup and updating of all buildings.
"""

from __future__ import annotations
from typing import Dict, Optional, List, TYPE_CHECKING
from src.buildings.building import Building
from src.buildings.building_types import get_building_def, get_cost

if TYPE_CHECKING:
    from src.core.grid import Grid
    from src.economy.economy import Economy


class BuildingManager:
    def __init__(self):
        self._buildings: Dict[int, Building] = {}
        self._next_id = 1

    # ------------------------------------------------------------------ placement

    def place(self, btype: str, col: int, row: int,
              grid: "Grid", economy: Optional["Economy"] = None,
              instant: bool = False) -> Optional[Building]:
        """
        Place a building on the grid. Returns the Building if successful,
        None if placement failed (tiles occupied, not enough money, etc.).
        """
        defn = get_building_def(btype)
        cost = get_cost(btype)

        # cost is an int (money)
        cost_money = cost if isinstance(cost, (int, float)) else cost.get("money", 0)

        # Economy check
        if economy and not instant:
            if not economy.can_afford(cost_money):
                return None

        # Road special case: just marks tile
        if btype == "road":
            if grid.place_road(col, row):
                bid = self._next_id; self._next_id += 1
                b = Building(id=bid, building_type="road", col=col, row=row)
                b.instant_build()
                self._buildings[bid] = b
                if economy and not instant:
                    economy.spend(cost_money)
                return b
            return None

        # Normal building
        if not grid.place_building(col, row, 0, defn.width, defn.height):
            return None  # tiles occupied or invalid

        bid = self._next_id; self._next_id += 1
        b = Building(id=bid, building_type=btype, col=col, row=row)
        # Stamp real id
        for dc in range(defn.width):
            for dr in range(defn.height):
                t = grid.get(col+dc, row+dr)
                if t:
                    t.building_id = bid

        if instant:
            b.instant_build()

        self._buildings[bid] = b

        if economy and not instant:
            economy.spend(cost_money)

        return b

    def demolish(self, building_id: int, grid: "Grid",
                 economy: Optional["Economy"] = None) -> bool:
        b = self._buildings.get(building_id)
        if not b:
            return False
        grid.remove_building(b.col, b.row, b.width, b.height)
        # Refund 50%
        if economy:
            cost = get_cost(b.building_type)
            cost_money = cost if isinstance(cost, (int, float)) else cost.get("money", 0)
            economy.add_money(cost_money * 0.5)
        del self._buildings[building_id]
        return True

    # ------------------------------------------------------------------ update

    def update(self, sim_ticks: int):
        for b in self._buildings.values():
            b.update(sim_ticks)

    # ------------------------------------------------------------------ queries

    def get(self, building_id: int) -> Optional[Building]:
        return self._buildings.get(building_id)

    def all_buildings(self) -> List[Building]:
        return list(self._buildings.values())

    def buildings_of_type(self, btype: str) -> List[Building]:
        return [b for b in self._buildings.values() if b.building_type == btype]

    def nearest_of_type(self, btype: str, col: float, row: float) -> Optional[Building]:
        import math
        candidates = [b for b in self.buildings_of_type(btype) if b.is_complete]
        if not candidates:
            return None
        return min(candidates, key=lambda b: math.hypot(b.col - col, b.row - row))

    def available_jobs(self) -> List[Building]:
        return [b for b in self._buildings.values() if b.has_free_job]

    def available_homes(self) -> List[Building]:
        return [b for b in self._buildings.values() if b.has_free_home]

    def total_housing(self) -> int:
        return sum(b.definition.provides_housing for b in self._buildings.values() if b.is_complete)

    def total_jobs(self) -> int:
        return sum(b.definition.provides_jobs for b in self._buildings.values() if b.is_complete)

    def total_food_production(self) -> float:
        return sum(b.definition.food_production for b in self._buildings.values() if b.is_complete)

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            "next_id": self._next_id,
            "buildings": [b.to_dict() for b in self._buildings.values()]
        }

    @classmethod
    def from_dict(cls, d):
        bm = cls()
        bm._next_id = d.get("next_id", 1)
        for bd in d.get("buildings", []):
            b = Building.from_dict(bd)
            bm._buildings[b.id] = b
        return bm