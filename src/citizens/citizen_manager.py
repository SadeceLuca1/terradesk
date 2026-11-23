"""
TerraDesk – Citizen Manager
Manages all citizens: spawning, updating, assigning jobs/homes.
"""

from __future__ import annotations
import random
from typing import Dict, List, Optional, TYPE_CHECKING
from src.citizens.citizen import Citizen

if TYPE_CHECKING:
    from src.core.game import Game


class CitizenManager:
    def __init__(self):
        self._citizens: Dict[int, Citizen] = {}

    # ------------------------------------------------------------------ spawning

    def spawn(self, game: "Game", col: Optional[int] = None,
              row: Optional[int] = None) -> Citizen:
        c = Citizen()
        if col is not None:
            c.x = float(col)
        if row is not None:
            c.y = float(row)
        else:
            # Place near existing citizens or centre
            if self._citizens:
                ref = random.choice(list(self._citizens.values()))
                c.x = ref.x + random.uniform(-3, 3)
                c.y = ref.y + random.uniform(-3, 3)
            else:
                c.x = game.grid.cols / 2 + random.uniform(-5, 5)
                c.y = game.grid.rows / 2 + random.uniform(-5, 5)

        # Clamp to grid
        c.x = max(2, min(game.grid.cols - 3, c.x))
        c.y = max(2, min(game.grid.rows - 3, c.y))

        self._citizens[c.id] = c
        self._auto_assign(c, game)
        return c

    def _auto_assign(self, c: Citizen, game):
        """Try to assign a home and a job to a new citizen."""
        bm = game.building_manager
        # Home
        homes = bm.available_homes()
        if homes:
            home = random.choice(homes)
            if home.add_resident(c.id):
                c.home_id = home.id

        # Job
        jobs = bm.available_jobs()
        if jobs:
            job = random.choice(jobs)
            if job.add_worker(c.id):
                c.workplace_id = job.id

    # ------------------------------------------------------------------ update

    def update(self, dt: float, game: "Game"):
        sim_speed = game.time_manager.speed if not game.time_manager.paused else 0
        for c in self._citizens.values():
            c.update(dt, sim_speed, game)

        # Periodic auto-assignment of homeless/unemployed
        if game.time_manager.tick % 600 == 0:
            self._reassign_all(game)

    def _reassign_all(self, game):
        bm = game.building_manager
        for c in self._citizens.values():
            if c.home_id is None or bm.get(c.home_id) is None:
                homes = bm.available_homes()
                if homes:
                    home = random.choice(homes)
                    if home.add_resident(c.id):
                        c.home_id = home.id
            if c.workplace_id is None or bm.get(c.workplace_id) is None:
                jobs = bm.available_jobs()
                if jobs:
                    job = random.choice(jobs)
                    if job.add_worker(c.id):
                        c.workplace_id = job.id

    # ------------------------------------------------------------------ queries

    def get(self, cid: int) -> Optional[Citizen]:
        return self._citizens.get(cid)

    def all_citizens(self) -> List[Citizen]:
        return list(self._citizens.values())

    def citizens_at(self, col: int, row: int) -> List[Citizen]:
        return [c for c in self._citizens.values()
                if c.tile_col == col and c.tile_row == row]

    def citizen_near(self, px: float, py: float,
                     camera, threshold: float = 20.0) -> Optional[Citizen]:
        """Find citizen whose screen position is near (px,py)."""
        import math
        best = None
        best_dist = threshold
        for c in self._citizens.values():
            sx, sy = camera.world_to_screen(c.x, c.y)
            d = math.hypot(sx - px, sy - py)
            if d < best_dist:
                best_dist = d
                best = c
        return best

    @property
    def count(self):
        return len(self._citizens)

    @property
    def average_happiness(self):
        if not self._citizens:
            return 0.0
        return sum(c.happiness for c in self._citizens.values()) / len(self._citizens)

    # ------------------------------------------------------------------ manual controls

    def remove(self, cid: int, game):
        c = self._citizens.pop(cid, None)
        if c:
            if c.home_id:
                home = game.building_manager.get(c.home_id)
                if home: home.remove_resident(cid)
            if c.workplace_id:
                wp = game.building_manager.get(c.workplace_id)
                if wp: wp.remove_worker(cid)

    def set_happiness(self, cid: int, value: float):
        c = self._citizens.get(cid)
        if c:
            c.happiness = max(0.0, min(1.0, value))

    def set_all_happiness(self, value: float):
        for c in self._citizens.values():
            c.happiness = max(0.0, min(1.0, value))

    def assign_job(self, cid: int, building_id: int, game) -> bool:
        c = self._citizens.get(cid)
        bld = game.building_manager.get(building_id)
        if not c or not bld:
            return False
        # Remove from old job
        if c.workplace_id:
            old = game.building_manager.get(c.workplace_id)
            if old: old.remove_worker(cid)
        if bld.add_worker(cid):
            c.workplace_id = building_id
            return True
        return False

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            "id_counter": Citizen._id_counter,
            "citizens": [c.to_dict() for c in self._citizens.values()]
        }

    @classmethod
    def from_dict(cls, d):
        cm = cls()
        Citizen._id_counter = d.get("id_counter", 0)
        for cd in d.get("citizens", []):
            c = Citizen.from_dict(cd)
            cm._citizens[c.id] = c
        return cm