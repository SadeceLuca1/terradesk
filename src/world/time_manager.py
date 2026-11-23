"""
TerraDesk – Time Manager
In-game clock: hours, days, seasons, years.
Dynamic sky colour based on time of day.
"""

from __future__ import annotations
import pygame
from src.core.constants import (
    TICKS_PER_MINUTE, HOURS_PER_DAY, DAYS_PER_SEASON, SEASONS_PER_YEAR,
    SIM_SPEEDS, C_SKY_DAY, C_SKY_DAWN, C_SKY_DUSK, C_SKY_NIGHT, C_SKY_MIDNIGHT,
)

SEASONS = ["spring", "summer", "autumn", "winter"]


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class TimeManager:
    def __init__(self):
        self.tick: int = 0           # absolute sim tick
        self.minute: int = 0
        self.hour: int = 7           # start at 7 AM
        self.day: int = 1
        self.season_index: int = 0   # 0=spring … 3=winter
        self.year: int = 1

        self.paused: bool = False
        self.speed_index: int = 1    # index into SIM_SPEEDS
        self._tick_accum: float = 0.0

    # ------------------------------------------------------------------ update

    def update(self, dt: float):
        if self.paused:
            return
        spd = SIM_SPEEDS[self.speed_index]
        self._tick_accum += dt * spd * TICKS_PER_MINUTE
        while self._tick_accum >= 1.0:
            self._tick_accum -= 1.0
            self._advance_tick()

    def _advance_tick(self):
        self.tick += 1
        self.minute += 1
        if self.minute >= 60:
            self.minute = 0
            self.hour += 1
            if self.hour >= HOURS_PER_DAY:
                self.hour = 0
                self.day += 1
                if self.day > DAYS_PER_SEASON:
                    self.day = 1
                    self.season_index = (self.season_index + 1) % SEASONS_PER_YEAR
                    if self.season_index == 0:
                        self.year += 1

    # ------------------------------------------------------------------ controls

    def toggle_pause(self):
        self.paused = not self.paused

    def set_speed(self, index: int):
        self.speed_index = max(0, min(len(SIM_SPEEDS) - 1, index))
        if index > 0:
            self.paused = False

    def speed_up(self):
        self.set_speed(self.speed_index + 1)

    def speed_down(self):
        self.set_speed(self.speed_index - 1)

    # ------------------------------------------------------------------ properties

    @property
    def speed(self) -> int:
        return SIM_SPEEDS[self.speed_index]

    @property
    def season(self) -> str:
        return SEASONS[self.season_index]

    @property
    def time_string(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"

    @property
    def date_string(self) -> str:
        return f"Day {self.day}  {self.season.capitalize()}  Year {self.year}"

    @property
    def sky_color(self):
        """Return interpolated sky colour based on hour."""
        h = self.hour + self.minute / 60.0
        if h < 5:
            return _lerp_color(C_SKY_MIDNIGHT, C_SKY_NIGHT, h / 5)
        if h < 7:
            return _lerp_color(C_SKY_NIGHT, C_SKY_DAWN, (h - 5) / 2)
        if h < 9:
            return _lerp_color(C_SKY_DAWN, C_SKY_DAY, (h - 7) / 2)
        if h < 18:
            return C_SKY_DAY
        if h < 20:
            return _lerp_color(C_SKY_DAY, C_SKY_DUSK, (h - 18) / 2)
        if h < 22:
            return _lerp_color(C_SKY_DUSK, C_SKY_NIGHT, (h - 20) / 2)
        return _lerp_color(C_SKY_NIGHT, C_SKY_MIDNIGHT, (h - 22) / 2)

    @property
    def is_day(self) -> bool:
        return 6 <= self.hour < 20

    @property
    def darkness(self) -> float:
        """0.0=full day  1.0=full night for rendering overlays."""
        h = self.hour + self.minute / 60.0
        if 8 <= h <= 17:
            return 0.0
        if 6 <= h < 8:
            return 1.0 - (h - 6) / 2
        if 17 < h <= 20:
            return (h - 17) / 3
        return 1.0

    @property
    def window_light(self) -> bool:
        """Should building windows glow?"""
        return self.darkness > 0.3

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            'tick': self.tick, 'minute': self.minute, 'hour': self.hour,
            'day': self.day, 'season': self.season_index, 'year': self.year,
            'speed': self.speed_index,
        }

    @classmethod
    def from_dict(cls, d):
        tm = cls()
        tm.tick = d.get('tick', 0)
        tm.minute = d.get('minute', 0)
        tm.hour = d.get('hour', 7)
        tm.day = d.get('day', 1)
        tm.season_index = d.get('season', 0)
        tm.year = d.get('year', 1)
        tm.speed_index = d.get('speed', 1)
        return tm