"""
TerraDesk – Building
Individual building instance with state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from src.buildings.building_types import get_building_def, get_cost


@dataclass
class Building:
    id: int
    building_type: str
    col: int
    row: int

    # Footprint (from definition)
    width: int = 1
    height: int = 1

    # Construction
    under_construction: bool = True
    construction_progress: float = 0.0   # 0.0 → 1.0
    construction_ticks: int = 0
    construction_duration: int = 300     # sim ticks to build

    # Operational
    active: bool = False
    workers: List[int] = field(default_factory=list)   # citizen IDs
    residents: List[int] = field(default_factory=list) # citizen IDs (houses)
    level: int = 1
    health: float = 1.0

    # Economy
    daily_income: float = 0.0
    daily_upkeep: float = 0.0

    def __post_init__(self):
        defn = get_building_def(self.building_type)
        self.width = defn.width
        self.height = defn.height
        cost_ticks = {"house":200,"farm":300,"market":400,"school":500,
                      "hospital":600,"church":450,"tavern":250,"well":100,
                      "mill":350,"blacksmith":300,"warehouse":280,
                      "road":30,"tree":20,"bridge":200}
        self.construction_duration = cost_ticks.get(self.building_type, 300)
        self.daily_upkeep = get_cost(self.building_type).get("money", 100) * 0.01

    # ------------------------------------------------------------------ update

    def update(self, sim_ticks: int):
        if self.under_construction:
            self.construction_ticks += 1
            self.construction_progress = min(
                1.0, self.construction_ticks / self.construction_duration
            )
            if self.construction_progress >= 1.0:
                self.under_construction = False
                self.active = True

    # ------------------------------------------------------------------ helpers

    @property
    def definition(self):
        return get_building_def(self.building_type)

    @property
    def is_complete(self):
        return not self.under_construction

    @property
    def max_workers(self):
        return self.definition.provides_jobs

    @property
    def max_residents(self):
        return self.definition.provides_housing

    @property
    def has_free_job(self):
        return len(self.workers) < self.max_workers and self.active

    @property
    def has_free_home(self):
        return len(self.residents) < self.max_residents and self.active

    def add_worker(self, cid: int):
        if len(self.workers) < self.max_workers:
            self.workers.append(cid)
            return True
        return False

    def remove_worker(self, cid: int):
        if cid in self.workers:
            self.workers.remove(cid)

    def add_resident(self, cid: int):
        if len(self.residents) < self.max_residents:
            self.residents.append(cid)
            return True
        return False

    def remove_resident(self, cid: int):
        if cid in self.residents:
            self.residents.remove(cid)

    def instant_build(self):
        self.under_construction = False
        self.construction_progress = 1.0
        self.active = True

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.building_type,
            "col": self.col,
            "row": self.row,
            "width": self.width,
            "height": self.height,
            "under_construction": self.under_construction,
            "construction_progress": self.construction_progress,
            "construction_ticks": self.construction_ticks,
            "active": self.active,
            "workers": self.workers,
            "residents": self.residents,
            "level": self.level,
            "health": self.health,
        }

    @classmethod
    def from_dict(cls, d):
        b = cls(
            id=d["id"],
            building_type=d["type"],
            col=d["col"],
            row=d["row"],
        )
        b.under_construction = d.get("under_construction", False)
        b.construction_progress = d.get("construction_progress", 1.0)
        b.construction_ticks = d.get("construction_ticks", b.construction_duration)
        b.active = d.get("active", True)
        b.workers = d.get("workers", [])
        b.residents = d.get("residents", [])
        b.level = d.get("level", 1)
        b.health = d.get("health", 1.0)
        return b