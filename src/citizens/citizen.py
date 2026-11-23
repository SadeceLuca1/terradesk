"""
TerraDesk – Citizen
Individual citizen with identity, needs, AI state.
"""

from __future__ import annotations
import random
import math
from typing import Optional, List, Tuple
from src.core.constants import (
    NEED_HUNGER_DECAY, NEED_ENERGY_DECAY, NEED_SOCIAL_DECAY,
    NEED_HAPPINESS_DECAY, AI_THINK_INTERVAL, C_CITIZEN_SHIRT,
    C_CITIZEN_PANTS, C_CITIZEN_HAIR_1, C_CITIZEN_HAIR_2, C_CITIZEN_HAIR_3
)

FIRST_NAMES = [
    "Alice","Bob","Clara","Dani","Elara","Finn","Gina","Hugo","Iris","Jake",
    "Kira","Leo","Mara","Noah","Ora","Percy","Quinn","Rosa","Sam","Tara",
    "Uma","Vince","Wren","Xena","Yara","Zoe","Aiden","Beth","Cody","Dawn",
    "Evan","Faye","Glen","Hana","Ivan","Jade","Karl","Luna","Marc","Nina",
]
LAST_NAMES = [
    "Smith","Miller","Brown","Davis","Wilson","Moore","Taylor","Anderson",
    "Thomas","Jackson","White","Harris","Martin","Garcia","Lee","Walker",
    "Hall","Allen","Young","King","Wright","Scott","Green","Baker","Adams",
]
PROFESSIONS = [
    "Farmer","Blacksmith","Merchant","Teacher","Doctor","Builder","Lumberjack",
    "Baker","Tailor","Innkeeper","Guard","Fisher","Herbalist","Carpenter",
    "Shepherd","Miner","Cook","Priest","Trader","Wanderer",
]
PERSONALITIES = [
    "Cheerful","Grumpy","Hardworking","Lazy","Curious","Shy","Brave",
    "Cautious","Generous","Stingy","Adventurous","Homebody","Sociable","Loner",
]

AI_STATES = [
    "idle","moving","working","eating","sleeping","socialising","wandering",
    "going_home","going_work","going_market","going_tavern","going_church",
]

_RNG = random.Random()


class Citizen:
    _id_counter = 0

    @classmethod
    def _next_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def __init__(self, name: Optional[str] = None, age: Optional[int] = None):
        self.id = Citizen._next_id()
        # Identity
        rng = _RNG
        self.first_name = name or rng.choice(FIRST_NAMES)
        self.last_name = rng.choice(LAST_NAMES)
        self.age = age if age is not None else rng.randint(18, 65)
        self.personality = rng.choice(PERSONALITIES)
        self.profession = rng.choice(PROFESSIONS)

        # Visual
        hair_colors = [C_CITIZEN_HAIR_1, C_CITIZEN_HAIR_2, C_CITIZEN_HAIR_3,
                       (170,130,80),(80,50,30),(200,200,200)]
        self.hair_color = rng.choice(hair_colors)
        self.shirt_color = rng.choice(C_CITIZEN_SHIRT)
        self.pants_color = rng.choice(C_CITIZEN_PANTS)

        # World position (float for smooth movement)
        self.x: float = float(rng.randint(10, 50))
        self.y: float = float(rng.randint(10, 50))

        # Path
        self._path: List[Tuple[int,int]] = []
        self._path_index: int = 0
        self.move_speed: float = rng.uniform(0.03, 0.06)

        # Assignments
        self.home_id: Optional[int] = None
        self.workplace_id: Optional[int] = None
        self.family_ids: List[int] = []
        self.friend_ids: List[int] = []

        # Needs (0.0=empty, 1.0=full)
        self.hunger: float = rng.uniform(0.5, 1.0)
        self.energy: float = rng.uniform(0.5, 1.0)
        self.social: float = rng.uniform(0.3, 0.8)
        self.happiness: float = rng.uniform(0.5, 0.9)

        # AI
        self.state: str = "idle"
        self.state_timer: int = 0
        self._think_timer: int = rng.randint(0, AI_THINK_INTERVAL)
        self.target_col: Optional[int] = None
        self.target_row: Optional[int] = None

        # Economy
        self.money: float = rng.uniform(10, 50)
        self.salary: float = 50.0

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def tile_col(self):
        return int(self.x)

    @property
    def tile_row(self):
        return int(self.y)

    # ------------------------------------------------------------------ update

    def update(self, dt: float, sim_speed: float, game):
        if sim_speed == 0:
            return

        self._decay_needs(sim_speed)
        self._update_happiness()
        self._move(sim_speed)

        self._think_timer -= 1
        if self._think_timer <= 0:
            self._think_timer = AI_THINK_INTERVAL + _RNG.randint(-30, 30)
            self._think(game)

        self.state_timer += 1

    def _decay_needs(self, sim_speed: float):
        s = sim_speed * 0.016  # ~1 frame at speed 1
        self.hunger = max(0.0, self.hunger - NEED_HUNGER_DECAY * s)
        self.energy = max(0.0, self.energy - NEED_ENERGY_DECAY * s)
        self.social = max(0.0, self.social - NEED_SOCIAL_DECAY * s)

    def _update_happiness(self):
        """Happiness is a weighted average of needs."""
        h = (self.hunger * 0.35 + self.energy * 0.30 +
             self.social * 0.20 + self.happiness * 0.15)
        # Personality modifier
        mods = {"Cheerful": 0.05, "Grumpy": -0.08, "Shy": -0.02,
                "Sociable": 0.03, "Homebody": 0.02}
        h = max(0.0, min(1.0, h + mods.get(self.personality, 0.0)))
        # Smooth transition
        self.happiness = self.happiness * 0.95 + h * 0.05

    def _think(self, game):
        """Decide next action based on current needs and time."""
        tm = game.time_manager
        hour = tm.hour
        bm = game.building_manager

        # Sleep at night
        if hour >= 22 or hour < 6:
            if self.state != "sleeping":
                self._go_home(bm)
                self.state = "sleeping"
            return

        # Critical hunger
        if self.hunger < 0.2:
            market = bm.nearest_of_type("market", self.x, self.y)
            if market:
                self._set_target(market.col, market.row, game)
                self.state = "going_market"
            return

        # Low energy – rest
        if self.energy < 0.15 and hour > 12:
            self._go_home(bm)
            self.state = "going_home"
            return

        # Work hours: 8-17
        if 8 <= hour < 17:
            if self.workplace_id and self.state not in ("working",):
                wp = bm.get(self.workplace_id)
                if wp:
                    self._set_target(wp.col, wp.row, game)
                    self.state = "going_work"
            elif not self.workplace_id:
                self.state = "wandering"
                self._wander(game)
            return

        # Social time: 17-20
        if 17 <= hour < 20:
            if self.social < 0.5:
                tavern = bm.nearest_of_type("tavern", self.x, self.y)
                if tavern:
                    self._set_target(tavern.col, tavern.row, game)
                    self.state = "going_tavern"
                    return
            self._wander(game)
            return

        # Default – wander
        if self.state == "idle" or self.state_timer > 300:
            self._wander(game)

    def _go_home(self, bm):
        home = bm.get(self.home_id) if self.home_id else None
        if home:
            self.target_col = home.col
            self.target_row = home.row

    def _set_target(self, col: int, row: int, game):
        from src.citizens.pathfinding import find_path
        path = find_path(game.grid, (self.tile_col, self.tile_row), (col, row))
        if path:
            self._path = path
            self._path_index = 0
        self.target_col = col
        self.target_row = row

    def _wander(self, game):
        import random
        col = max(2, min(game.grid.cols-3, self.tile_col + random.randint(-6, 6)))
        row = max(2, min(game.grid.rows-3, self.tile_row + random.randint(-6, 6)))
        t = game.grid.get(col, row)
        if t and t.walkable:
            self._set_target(col, row, game)
            self.state = "wandering"

    def _move(self, sim_speed: float):
        """Follow path smoothly."""
        if not self._path or self._path_index >= len(self._path):
            if self.state in ("going_home","going_work","going_market",
                              "going_tavern","going_church","moving","wandering"):
                if self.state == "going_work":
                    self.state = "working"
                    self.state_timer = 0
                elif self.state == "going_market":
                    self.hunger = min(1.0, self.hunger + 0.6)
                    self.state = "idle"
                elif self.state == "going_tavern":
                    self.social = min(1.0, self.social + 0.5)
                    self.happiness = min(1.0, self.happiness + 0.1)
                    self.state = "socialising"
                    self.state_timer = 0
                elif self.state in ("going_home","sleeping"):
                    self.energy = min(1.0, self.energy + 0.4 * sim_speed * 0.016)
                    self.state = "sleeping"
                else:
                    self.state = "idle"
                    self.state_timer = 0
            return

        target = self._path[self._path_index]
        tc, tr = target
        spd = self.move_speed * sim_speed

        dx = tc - self.x
        dy = tr - self.y
        dist = math.hypot(dx, dy)
        if dist < spd:
            self.x = float(tc)
            self.y = float(tr)
            self._path_index += 1
        else:
            self.x += (dx / dist) * spd
            self.y += (dy / dist) * spd

        # Working restores energy slowly
        if self.state == "working":
            self.energy = min(1.0, self.energy + 0.001 * sim_speed * 0.016)
            self.money += self.salary / (8 * 60 * 60) * sim_speed

    # ------------------------------------------------------------------ info

    def get_info_dict(self):
        return {
            "Name": self.name,
            "Age": self.age,
            "Profession": self.profession,
            "Personality": self.personality,
            "State": self.state.replace("_"," ").capitalize(),
            "Hunger": f"{self.hunger*100:.0f}%",
            "Energy": f"{self.energy*100:.0f}%",
            "Social": f"{self.social*100:.0f}%",
            "Happiness": f"{self.happiness*100:.0f}%",
            "Money": f"${self.money:.0f}",
        }

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "personality": self.personality,
            "profession": self.profession,
            "hair_color": list(self.hair_color),
            "shirt_color": list(self.shirt_color),
            "pants_color": list(self.pants_color),
            "x": self.x,
            "y": self.y,
            "home_id": self.home_id,
            "workplace_id": self.workplace_id,
            "hunger": self.hunger,
            "energy": self.energy,
            "social": self.social,
            "happiness": self.happiness,
            "money": self.money,
            "salary": self.salary,
        }

    @classmethod
    def from_dict(cls, d):
        c = cls.__new__(cls)
        c.id = d["id"]
        c.first_name = d["first_name"]
        c.last_name = d["last_name"]
        c.age = d["age"]
        c.personality = d["personality"]
        c.profession = d["profession"]
        c.hair_color = tuple(d["hair_color"])
        c.shirt_color = tuple(d["shirt_color"])
        c.pants_color = tuple(d["pants_color"])
        c.x = d["x"]
        c.y = d["y"]
        c._path = []
        c._path_index = 0
        c.move_speed = _RNG.uniform(0.03, 0.06)
        c.home_id = d.get("home_id")
        c.workplace_id = d.get("workplace_id")
        c.family_ids = []
        c.friend_ids = []
        c.hunger = d.get("hunger", 0.8)
        c.energy = d.get("energy", 0.8)
        c.social = d.get("social", 0.6)
        c.happiness = d.get("happiness", 0.7)
        c.money = d.get("money", 20)
        c.salary = d.get("salary", 50)
        c.state = "idle"
        c.state_timer = 0
        c._think_timer = _RNG.randint(0, AI_THINK_INTERVAL)
        c.target_col = None
        c.target_row = None
        # Restore class counter
        if c.id >= Citizen._id_counter:
            Citizen._id_counter = c.id
        return c