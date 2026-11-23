"""
TerraDesk – HUD (Heads-Up Display)
Notifications, tooltips, build ghost, selection hints.
"""
from __future__ import annotations
import math
import pygame
from typing import TYPE_CHECKING
from src.core.constants import (
    TOOLBAR_HEIGHT, SIDEBAR_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    C_UI_TEXT, C_UI_TEXT_DIM, C_UI_PANEL, C_UI_BORDER, C_UI_ACCENT,
    C_UI_SUCCESS, C_UI_WARNING, C_UI_DANGER, PANEL_PADDING,
    TILE_HALF_W, TILE_HALF_H,
)
from src.ui.ui_base import font, draw_panel

if TYPE_CHECKING:
    from src.core.game import Game


class Notification:
    __slots__ = ('text', 'color', 'duration', 'age', 'fade_start')

    def __init__(self, text: str, color=C_UI_TEXT, duration: float = 3.0):
        self.text = text
        self.color = color
        self.duration = duration
        self.age = 0.0
        self.fade_start = duration * 0.7

    @property
    def alive(self) -> bool:
        return self.age < self.duration

    @property
    def alpha(self) -> int:
        if self.age < self.fade_start:
            return 255
        t = (self.age - self.fade_start) / (self.duration - self.fade_start)
        return max(0, int(255 * (1 - t)))


class HUD:
    MAX_NOTIFS = 5

    def __init__(self):
        self._notifs: list[Notification] = []
        self._tooltip: str = ""
        self._tooltip_pos: tuple[int, int] = (0, 0)

    # ── Notifications ────────────────────────────────────────────────────────

    def add_notification(self, text: str, color=C_UI_TEXT, duration: float = 3.0):
        self._notifs.insert(0, Notification(text, color, duration))
        self._notifs = self._notifs[:self.MAX_NOTIFS]

    def set_tooltip(self, text: str, pos: tuple[int, int]):
        self._tooltip = text
        self._tooltip_pos = pos

    def clear_tooltip(self):
        self._tooltip = ""

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float):
        for n in self._notifs:
            n.age += dt
        self._notifs = [n for n in self._notifs if n.alive]

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface, game: "Game"):
        self._draw_notifications(surf)
        if self._tooltip:
            self._draw_tooltip(surf)
        self._draw_build_ghost(surf, game)
        self._draw_selection_hint(surf, game)

    def _draw_notifications(self, surf: pygame.Surface):
        x = PANEL_PADDING
        y = TOOLBAR_HEIGHT + PANEL_PADDING
        f = font(12)
        for n in self._notifs:
            s = f.render(n.text, True, n.color)
            s.set_alpha(n.alpha)
            # Semi-transparent background
            bg = pygame.Surface((s.get_width() + 10, s.get_height() + 4), pygame.SRCALPHA)
            bg.fill((10, 12, 20, int(n.alpha * 0.7)))
            surf.blit(bg, (x - 2, y - 1))
            surf.blit(s, (x + 3, y + 1))
            y += s.get_height() + 4

    def _draw_tooltip(self, surf: pygame.Surface):
        f = font(11)
        lines = self._tooltip.split("\n")
        w = max(f.size(l)[0] for l in lines) + 12
        h = sum(f.get_height() for _ in lines) + 8
        tx, ty = self._tooltip_pos
        tx = min(tx + 12, WINDOW_WIDTH - SIDEBAR_WIDTH - w - 4)
        ty = max(ty - h - 4, TOOLBAR_HEIGHT + 4)
        draw_panel(surf, pygame.Rect(tx, ty, w, h))
        for i, line in enumerate(lines):
            s = f.render(line, True, C_UI_TEXT)
            surf.blit(s, (tx + 6, ty + 4 + i * f.get_height()))

    def _draw_build_ghost(self, surf: pygame.Surface, game: "Game"):
        if game.mode != "build" or not game.selected_building_type:
            return
        btype = game.selected_building_type
        cam = game.camera
        mx, my = pygame.mouse.get_pos()
        col, row = cam.screen_to_tile(mx, my - TOOLBAR_HEIGHT)

        from src.buildings.building_types import get_building_def
        bdef = get_building_def(btype)
        if not bdef:
            return

        # Check can place
        can_place = True
        for dc in range(bdef.width):
            for dr in range(bdef.height):
                t = game.grid.get(col + dc, row + dr)
                if not t or not t.buildable or t.building_id is not None:
                    can_place = False
                    break

        z = cam.zoom
        hw = int(TILE_HALF_W * z)
        hh = int(TILE_HALF_H * z)
        alpha = 140
        color = (80, 200, 80, alpha) if can_place else (200, 60, 60, alpha)

        for dc in range(bdef.width):
            for dr in range(bdef.height):
                sx, sy = cam.world_to_screen(col + dc, row + dr)
                sx, sy = int(sx), int(sy)
                pts = [(sx, sy - hh), (sx + hw, sy), (sx, sy + hh), (sx - hw, sy)]
                s = pygame.Surface((hw * 2 + 2, hh * 2 + 2), pygame.SRCALPHA)
                s_pts = [(hw + 1, 1), (hw * 2 + 1, hh + 1),
                         (hw + 1, hh * 2 + 1), (1, hh + 1)]
                pygame.draw.polygon(s, color, s_pts)
                surf.blit(s, (sx - hw - 1, sy - hh - 1))

    def _draw_selection_hint(self, surf: pygame.Surface, game: "Game"):
        if not hasattr(game, 'selected_citizen') or not game.selected_citizen:
            return
        cit = game.selected_citizen
        f = font(11)
        # Draw mini status bar at bottom of view
        bary = WINDOW_HEIGHT - 24
        barx = PANEL_PADDING
        info = (f"{cit.first_name} {cit.last_name}  |  "
                f"❤{cit.happiness:.0%}  "
                f"🍞{cit.hunger:.0%}  "
                f"💤{cit.energy:.0%}  "
                f"💬{cit.social:.0%}  "
                f"[{cit.state}]")
        s = f.render(info, True, C_UI_TEXT)
        bg = pygame.Surface((s.get_width() + 10, s.get_height() + 4), pygame.SRCALPHA)
        bg.fill((10, 12, 20, 180))
        surf.blit(bg, (barx - 2, bary - 2))
        surf.blit(s, (barx + 3, bary))
