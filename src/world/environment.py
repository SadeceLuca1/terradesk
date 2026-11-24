"""
TerraDesk – Environment Manager
Coordinates weather, time, and seasonal effects.
"""

from __future__ import annotations
import pygame
from src.world.weather import Weather
from src.world.time_manager import TimeManager


class Environment:
    def __init__(self):
        self.weather = Weather()

    def update(self, dt: float, time_manager: TimeManager, screen_w: int, screen_h: int):
        self.weather.update(dt, time_manager.season, screen_w, screen_h)

    def draw(self, surf: pygame.Surface, camera, game):
        self.weather.draw(surf, camera, game)

    def set_weather(self, weather_type: str):
        self.weather.set_weather(weather_type)

    @property
    def current_weather(self):
        return self.weather.current

    def to_dict(self):
        return {"weather": self.weather.to_dict()}

    @classmethod
    def from_dict(cls, d):
        env = cls()
        env.weather = Weather.from_dict(d.get("weather", {}))
        return env
