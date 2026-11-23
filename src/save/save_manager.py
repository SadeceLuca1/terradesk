"""
TerraDesk – Save Manager
JSON-based save/load system with multiple slots and autosave.
"""

from __future__ import annotations
import json
import os
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game import Game

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".terradesk", "saves")
AUTOSAVE_PATH = os.path.join(SAVE_DIR, "autosave.json")


class SaveManager:
    def __init__(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        self._last_autosave = time.time()

    def save(self, game: "Game", slot: int = 0) -> bool:
        path = AUTOSAVE_PATH if slot == 0 else os.path.join(SAVE_DIR, f"slot_{slot}.json")
        try:
            data = {
                "version": 1,
                "timestamp": time.time(),
                "grid": game.grid.to_dict(),
                "buildings": game.building_manager.to_dict(),
                "citizens": game.citizen_manager.to_dict(),
                "economy": game.economy.to_dict(),
                "time": game.time_manager.to_dict(),
                "environment": game.environment.to_dict(),
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[SaveManager] Save error: {e}")
            return False

    def load(self, game: "Game", slot: int = 0) -> bool:
        path = AUTOSAVE_PATH if slot == 0 else os.path.join(SAVE_DIR, f"slot_{slot}.json")
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            from src.core.grid import Grid
            from src.buildings.building_manager import BuildingManager
            from src.citizens.citizen_manager import CitizenManager
            from src.economy.economy import Economy
            from src.world.time_manager import TimeManager
            from src.world.environment import Environment

            game.grid = Grid.from_dict(data["grid"])
            game.building_manager = BuildingManager.from_dict(data["buildings"])
            game.citizen_manager = CitizenManager.from_dict(data["citizens"])
            game.economy = Economy.from_dict(data["economy"])
            game.time_manager = TimeManager.from_dict(data["time"])
            game.environment = Environment.from_dict(data["environment"])
            return True
        except Exception as e:
            print(f"[SaveManager] Load error: {e}")
            return False

    def autosave(self, game: "Game", interval: float = 300.0):
        now = time.time()
        if now - self._last_autosave >= interval:
            self.save(game, slot=0)
            self._last_autosave = now

    def save_exists(self, slot: int = 0) -> bool:
        path = AUTOSAVE_PATH if slot == 0 else os.path.join(SAVE_DIR, f"slot_{slot}.json")
        return os.path.exists(path)