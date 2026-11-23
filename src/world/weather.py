"""
TerraDesk – Weather System
Rain, snow, fog, storms, clear skies.
"""

from __future__ import annotations
import random
import math
import pygame
from src.core.constants import *


WEATHER_TYPES = ["clear", "cloudy", "rain", "heavy_rain", "snow", "storm", "fog"]

SEASON_WEIGHTS = {
    "spring": {"clear":30,"cloudy":25,"rain":30,"heavy_rain":5,"snow":5,"storm":3,"fog":2},
    "summer": {"clear":50,"cloudy":20,"rain":15,"heavy_rain":5,"snow":0,"storm":8,"fog":2},
    "autumn": {"clear":20,"cloudy":35,"rain":25,"heavy_rain":8,"snow":5,"storm":5,"fog":2},
    "winter": {"clear":25,"cloudy":30,"rain":5,"heavy_rain":0,"snow":35,"storm":3,"fog":2},
}


class WeatherParticle:
    __slots__ = ("x","y","vx","vy","alpha","size","ptype")
    def __init__(self, x,y,vx,vy,alpha,size,ptype):
        self.x,self.y,self.vx,self.vy = x,y,vx,vy
        self.alpha,self.size,self.ptype = alpha,size,ptype


class Weather:
    def __init__(self):
        self.current = "clear"
        self.next = "clear"
        self.transition = 0.0
        self.particles: list[WeatherParticle] = []
        self._change_timer = random.randint(1800, 7200)
        self.wind_x = 0.5
        self.wind_y = 2.5
        self.thunder_alpha = 0
        self.rng = random.Random()

    # ------------------------------------------------------------------ update

    def update(self, dt: float, season: str, screen_w: int, screen_h: int):
        self._change_timer -= 1
        if self._change_timer <= 0:
            self._pick_next_weather(season)
            self._change_timer = self.rng.randint(1800, 7200)

        if self.current != self.next:
            self.transition = min(1.0, self.transition + dt * 0.3)
            if self.transition >= 1.0:
                self.current = self.next
                self.transition = 0.0

        self._spawn_particles(screen_w, screen_h)
        self._update_particles(screen_h)

        # Thunder flash
        if self.current == "storm":
            if self.rng.random() < 0.002:
                self.thunder_alpha = 200
        if self.thunder_alpha > 0:
            self.thunder_alpha = max(0, self.thunder_alpha - 15)

    def _pick_next_weather(self, season: str):
        weights = SEASON_WEIGHTS.get(season, SEASON_WEIGHTS["summer"])
        types  = list(weights.keys())
        wts    = list(weights.values())
        self.next = self.rng.choices(types, weights=wts)[0]

    def _spawn_particles(self, sw: int, sh: int):
        spawn_counts = {
            "rain": 8, "heavy_rain": 20, "snow": 4, "storm": 25,
        }
        count = spawn_counts.get(self.current, 0)
        for _ in range(count):
            x = self.rng.randint(-20, sw + 20)
            y = -10
            if self.current in ("rain", "heavy_rain", "storm"):
                vx = self.wind_x + self.rng.uniform(-0.3, 0.3)
                vy = self.rng.uniform(8, 14)
                alpha = self.rng.randint(140, 200)
                size = self.rng.randint(2, 4)
                self.particles.append(WeatherParticle(x,y,vx,vy,alpha,size,"rain"))
            elif self.current == "snow":
                vx = self.rng.uniform(-0.5, 0.5)
                vy = self.rng.uniform(1.0, 2.5)
                alpha = self.rng.randint(160, 230)
                size = self.rng.randint(2, 5)
                self.particles.append(WeatherParticle(x,y,vx,vy,alpha,size,"snow"))

        # Cap particles
        if len(self.particles) > 1200:
            self.particles = self.particles[-1200:]

    def _update_particles(self, sh: int):
        alive = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            if p.ptype == "snow":
                p.x += math.sin(p.y * 0.05) * 0.3
            if p.y < sh + 20:
                alive.append(p)
        self.particles = alive

    # ------------------------------------------------------------------ draw

    def draw(self, surf: pygame.Surface, camera, game):
        w, h = surf.get_size()

        # Fog overlay
        if self.current == "fog":
            fog = pygame.Surface((w, h), pygame.SRCALPHA)
            fog.fill((200, 210, 220, 60))
            surf.blit(fog, (0, 0))

        # Rain / Snow particles
        particle_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for p in self.particles:
            if p.ptype == "rain":
                end_x = int(p.x + p.vx * 3)
                end_y = int(p.y + p.vy * 3)
                pygame.draw.line(particle_surf, (100, 150, 220, p.alpha),
                                 (int(p.x), int(p.y)), (end_x, end_y), 1)
            elif p.ptype == "snow":
                pygame.draw.circle(particle_surf, (220, 230, 255, p.alpha),
                                   (int(p.x), int(p.y)), p.size)
        surf.blit(particle_surf, (0, 0))

        # Thunder flash
        if self.thunder_alpha > 0:
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((200, 200, 255, self.thunder_alpha))
            surf.blit(flash, (0, 0))

        # Storm dark overlay
        if self.current == "storm":
            dark = pygame.Surface((w, h), pygame.SRCALPHA)
            dark.fill((0, 0, 30, 60))
            surf.blit(dark, (0, 0))

    # ------------------------------------------------------------------ controls

    def set_weather(self, weather_type: str):
        if weather_type in WEATHER_TYPES:
            self.current = weather_type
            self.next = weather_type
            self.particles.clear()

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {"current": self.current, "wind_x": self.wind_x, "wind_y": self.wind_y}

    @classmethod
    def from_dict(cls, d):
        w = cls()
        w.current = d.get("current", "clear")
        w.next = w.current
        w.wind_x = d.get("wind_x", 0.5)
        w.wind_y = d.get("wind_y", 2.5)
        return w