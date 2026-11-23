"""
TerraDesk – Toolbar
Top bar: logo, mode buttons, speed controls, time/date, weather, stats.
"""
from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
from src.core.constants import (
    WINDOW_WIDTH, TOOLBAR_HEIGHT, SIDEBAR_WIDTH,
    C_UI_PANEL, C_UI_BORDER, C_UI_TEXT, C_UI_TEXT_DIM,
    C_UI_BUTTON, C_UI_BUTTON_HOV, C_UI_BUTTON_ACT, C_UI_ACCENT,
    C_UI_SUCCESS, C_UI_WARNING, C_UI_DANGER, PANEL_PADDING,
    SIM_SPEED_LABELS,
)
from src.ui.ui_base import font, draw_button, draw_label, draw_panel

if TYPE_CHECKING:
    from src.core.game import Game

MODES = ["build", "citizens", "economy", "stats", "environment", "godmode", "settings"]
MODE_ICONS = ["🏗", "👥", "💰", "📊", "🌤", "⚡", "⚙"]
MODE_LABELS = ["Build", "Citizens", "Economy", "Stats", "Weather", "God", "Settings"]


class Toolbar:
    def __init__(self):
        self._btn_rects: list[pygame.Rect] = []
        self._speed_rects: list[pygame.Rect] = []
        self._pause_rect: pygame.Rect | None = None

    def draw(self, surf: pygame.Surface, game: "Game"):
        # Background
        bar = pygame.Rect(0, 0, WINDOW_WIDTH, TOOLBAR_HEIGHT)
        pygame.draw.rect(surf, C_UI_PANEL, bar)
        pygame.draw.line(surf, C_UI_BORDER, (0, TOOLBAR_HEIGHT - 1),
                         (WINDOW_WIDTH, TOOLBAR_HEIGHT - 1), 1)

        x = PANEL_PADDING
        # Logo
        f_logo = font(16)
        logo = f_logo.render("🏡 TerraDesk", True, C_UI_ACCENT)
        surf.blit(logo, (x, (TOOLBAR_HEIGHT - logo.get_height()) // 2))
        x += logo.get_width() + 20

        # Mode buttons
        self._btn_rects.clear()
        btn_w = 72
        btn_h = TOOLBAR_HEIGHT - 10
        for i, (label, icon) in enumerate(zip(MODE_LABELS, MODE_ICONS)):
            r = pygame.Rect(x, 5, btn_w, btn_h)
            self._btn_rects.append(r)
            active = game.mode == MODES[i]
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, f"{icon} {label}", active, hover, size=11)
            x += btn_w + 3

        x += 10

        # Speed buttons
        self._speed_rects.clear()
        for i, label in enumerate(SIM_SPEED_LABELS):
            r = pygame.Rect(x, 8, 32, TOOLBAR_HEIGHT - 16)
            self._speed_rects.append(r)
            active = game.time_manager.speed_index == i
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, label, active, hover, size=10)
            x += 35

        x += 10

        # Time & date
        tm = game.time_manager
        time_txt = tm.time_string
        date_txt = tm.date_string
        draw_label(surf, time_txt, x, 5, C_UI_ACCENT, 15)
        draw_label(surf, date_txt, x, 23, C_UI_TEXT_DIM, 10)
        x += 160

        # Weather
        wx = game.environment.current_weather
        wx_icon = {
            "clear": "☀", "cloudy": "⛅", "rain": "🌧",
            "heavy_rain": "⛈", "snow": "❄", "storm": "⛈", "fog": "🌫",
        }.get(wx, "☀")
        draw_label(surf, f"{wx_icon} {wx.replace('_',' ').title()}", x, 12, C_UI_TEXT_DIM, 11)
        x += 100

        # Money & pop
        money = f"${game.economy.money:,.0f}"
        pop = f"Pop: {game.citizen_manager.count}"
        draw_label(surf, money, x, 5, C_UI_SUCCESS if game.economy.money >= 0 else C_UI_DANGER, 13)
        draw_label(surf, pop, x, 22, C_UI_TEXT_DIM, 11)

    def handle_event(self, event: pygame.event.Event, game: "Game") -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        for i, r in enumerate(self._btn_rects):
            if r.collidepoint(event.pos):
                game.mode = MODES[i]
                return True
        for i, r in enumerate(self._speed_rects):
            if r.collidepoint(event.pos):
                game.time_manager.set_speed(i)
                return True
        return False

    def in_toolbar(self, pos: tuple[int, int]) -> bool:
        return pos[1] < TOOLBAR_HEIGHT