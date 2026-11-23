"""
TerraDesk – Sidebar
Right-side panel. Dispatches drawing and events by game mode.
"""
from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
from src.core.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_HEIGHT, SIDEBAR_WIDTH, PANEL_PADDING,
    C_UI_PANEL, C_UI_BORDER, C_UI_BUTTON, C_UI_BUTTON_HOV, C_UI_BUTTON_ACT,
    C_UI_TEXT, C_UI_TEXT_DIM, C_UI_ACCENT, C_UI_ACCENT2,
    C_UI_SUCCESS, C_UI_WARNING, C_UI_DANGER, BUILDING_COSTS,
    DESKTOP_ALWAYS_ON_TOP, DESKTOP_WALLPAPER_MODE, DESKTOP_CLICK_THROUGH,
)
from src.ui.ui_base import font, draw_panel, draw_label, draw_button, draw_progress_bar, Button, Slider
from src.buildings.building_types import BUILDING_CATALOGUE, CATEGORIES, get_cost

if TYPE_CHECKING:
    from src.core.game import Game

_LEFT = WINDOW_WIDTH - SIDEBAR_WIDTH
_TOP  = TOOLBAR_HEIGHT
_H    = WINDOW_HEIGHT - TOOLBAR_HEIGHT

# Category short labels
_CAT_LABELS = {
    "buildings": "🏠 Buildings",
    "production": "🌾 Production",
    "commerce": "🏪 Commerce",
    "services": "🏥 Services",
    "infrastructure": "🛤 Infra",
    "nature": "🌲 Nature",
}

# God mode actions
_GOD_ACTIONS = [
    ("Spawn 5 Citizens", "spawn5", C_UI_ACCENT),
    ("Add $1000", "add_money", C_UI_SUCCESS),
    ("Add Food +50", "add_food", C_UI_SUCCESS),
    ("Add Wood +50", "add_wood", C_UI_SUCCESS),
    ("Add Stone +50", "add_stone", C_UI_SUCCESS),
    ("Max Happiness", "happy_all", (220, 180, 50)),
    ("Feed All", "feed_all", (220, 180, 50)),
    ("Energise All", "energize_all", (220, 180, 50)),
    ("Complete Buildings", "build_all", C_UI_ACCENT),
    ("Meteor Strike!", "meteor", C_UI_DANGER),
    ("Set Sunrise", "sunrise", (255, 200, 80)),
    ("Set Sunset", "sunset", (200, 100, 50)),
]


class Sidebar:
    def __init__(self):
        self._cat_index: int = 0
        self._scroll_y: int = 0
        self._tax_slider = Slider(
            pygame.Rect(_LEFT + PANEL_PADDING, 0, SIDEBAR_WIDTH - PANEL_PADDING * 2, 20),
            0.0, 0.3, 0.10, "Tax"
        )
        self._hovered_btn: str = ""

    # ── Draw entry point ──────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface, game: "Game", mode: str):
        # Panel background
        panel = pygame.Rect(_LEFT, _TOP, SIDEBAR_WIDTH, _H)
        pygame.draw.rect(surf, C_UI_PANEL, panel)
        pygame.draw.line(surf, C_UI_BORDER, (_LEFT, _TOP), (_LEFT, _TOP + _H), 1)

        {
            "build":       self._draw_build,
            "citizens":    self._draw_citizens,
            "economy":     self._draw_economy,
            "stats":       self._draw_stats,
            "environment": self._draw_environment,
            "godmode":     self._draw_godmode,
            "settings":    self._draw_settings,
        }.get(mode, self._draw_build)(surf, game)

    # ── BUILD mode ────────────────────────────────────────────────────────────

    def _draw_build(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        f_h = font(13)

        # Category tabs
        cats = list(CATEGORIES)
        tab_w = (SIDEBAR_WIDTH - PANEL_PADDING * 2) // len(cats)
        for i, cat in enumerate(cats):
            r = pygame.Rect(x + i * tab_w, y, tab_w, 24)
            active = self._cat_index == i
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, _CAT_LABELS.get(cat, cat)[:4], active, hover, size=9)
        y += 30

        # Building list
        cat = cats[self._cat_index]
        for btype, bdef in BUILDING_CATALOGUE.items():
            if bdef.category != cat:
                continue
            cost = get_cost(btype)
            can_afford = game.economy.can_afford(cost)
            selected = game.selected_building_type == btype

            r = pygame.Rect(x, y - self._scroll_y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 54)
            if not (0 < r.bottom and r.top < _H + _TOP):
                y += 58
                continue

            hover = r.collidepoint(pygame.mouse.get_pos())
            bg = C_UI_BUTTON_ACT if selected else C_UI_BUTTON_HOV if hover else C_UI_BUTTON
            if not can_afford:
                bg = tuple(max(0, c - 20) for c in bg)
            pygame.draw.rect(surf, bg, r, border_radius=4)
            pygame.draw.rect(surf, C_UI_BORDER, r, 1, border_radius=4)

            # Icon + name
            icon_s = font(18).render(bdef.icon, True, C_UI_TEXT)
            surf.blit(icon_s, (r.x + 4, r.y + 4))
            name_s = font(12).render(bdef.name, True, C_UI_TEXT)
            surf.blit(name_s, (r.x + 32, r.y + 4))
            # Size + cost
            size_txt = f"{bdef.width}×{bdef.height}"
            cost_col = C_UI_SUCCESS if can_afford else C_UI_DANGER
            cost_s = font(11).render(f"${cost}  {size_txt}", True, cost_col)
            surf.blit(cost_s, (r.x + 32, r.y + 22))
            # Description
            desc_s = font(10).render(bdef.description[:32], True, C_UI_TEXT_DIM)
            surf.blit(desc_s, (r.x + 4, r.y + 38))
            y += 58

        y += PANEL_PADDING - self._scroll_y
        # Demolish button
        if game.selected_tile:
            col, row = game.selected_tile
            t = game.grid.get(col, row)
            if t and t.building_id:
                r = pygame.Rect(x, y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 28)
                hover = r.collidepoint(pygame.mouse.get_pos())
                draw_button(surf, r, "🗑 Demolish", False, hover,
                            color=C_UI_DANGER, text_color=C_UI_TEXT, size=11)
                y += 32

        # Cancel build
        if game.selected_building_type:
            r = pygame.Rect(x, _TOP + _H - 36, SIDEBAR_WIDTH - PANEL_PADDING * 2, 28)
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, "✕ Cancel", False, hover,
                        color=(80, 40, 40), size=11)

    # ── CITIZENS mode ─────────────────────────────────────────────────────────

    def _draw_citizens(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        draw_label(surf, "👥 Citizens", x, y, C_UI_ACCENT, 14)
        y += 22
        draw_label(surf, f"Population: {game.citizen_manager.count}", x, y, C_UI_TEXT, 12)
        y += 16
        avg_h = game.citizen_manager.average_happiness
        draw_label(surf, f"Avg Happiness:", x, y, C_UI_TEXT_DIM, 11)
        y += 14
        draw_progress_bar(surf, pygame.Rect(x, y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 8),
                          avg_h, C_UI_SUCCESS)
        y += 16

        # Selected citizen detail
        sc = getattr(game, 'selected_citizen', None)
        if sc:
            y += 4
            draw_panel(surf, pygame.Rect(x - 2, y, SIDEBAR_WIDTH - PANEL_PADDING, 130))
            draw_label(surf, f"{sc.first_name} {sc.last_name}", x + 2, y + 4, C_UI_ACCENT, 13)
            draw_label(surf, f"Age {sc.age}  •  {sc.profession}", x + 2, y + 20, C_UI_TEXT_DIM, 10)
            for i, (label, val, col) in enumerate([
                ("❤ Happiness", sc.happiness, C_UI_SUCCESS),
                ("🍞 Hunger", sc.hunger, C_UI_WARNING),
                ("💤 Energy", sc.energy, C_UI_ACCENT),
                ("💬 Social", sc.social, C_UI_ACCENT2),
            ]):
                draw_label(surf, label, x + 2, y + 36 + i * 22, C_UI_TEXT_DIM, 10)
                draw_progress_bar(surf,
                    pygame.Rect(x + 80, y + 37 + i * 22, SIDEBAR_WIDTH - PANEL_PADDING - 84, 8),
                    val, col)
            y += 134

        # Citizen roster
        draw_label(surf, "── Residents ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        for cit in list(game.citizen_manager.all_citizens())[:12]:
            is_sel = sc and sc.id == cit.id
            r = pygame.Rect(x, y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 22)
            if r.bottom > _TOP + _H - 4:
                break
            bg = C_UI_BUTTON_ACT if is_sel else C_UI_BUTTON
            hover = r.collidepoint(pygame.mouse.get_pos())
            if hover:
                bg = C_UI_BUTTON_HOV
            pygame.draw.rect(surf, bg, r, border_radius=3)
            name = f"{cit.first_name} {cit.last_name}"
            draw_label(surf, name, x + 4, y + 4, C_UI_TEXT, 10)
            draw_progress_bar(surf, pygame.Rect(x + 110, y + 7, 60, 7), cit.happiness, C_UI_SUCCESS)
            state_col = {
                'working': C_UI_SUCCESS, 'sleeping': C_UI_ACCENT,
                'eating': C_UI_WARNING, 'socialising': C_UI_ACCENT2,
            }.get(cit.state, C_UI_TEXT_DIM)
            draw_label(surf, cit.state[:8], x + 174, y + 4, state_col, 9)
            y += 24

    # ── ECONOMY mode ──────────────────────────────────────────────────────────

    def _draw_economy(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        eco = game.economy
        draw_label(surf, "💰 Economy", x, y, C_UI_ACCENT, 14)
        y += 24
        col_v = C_UI_SUCCESS if eco.money >= 0 else C_UI_DANGER
        draw_label(surf, f"Treasury: ${eco.money:,.0f}", x, y, col_v, 13)
        y += 18
        draw_label(surf, f"Daily Income:  ${eco.day_income:,.0f}", x, y, C_UI_SUCCESS, 11)
        y += 14
        draw_label(surf, f"Daily Expenses: ${eco.day_expenses:,.0f}", x, y, C_UI_DANGER, 11)
        y += 20

        # Tax slider
        self._tax_slider.rect = pygame.Rect(x, y + 16, SIDEBAR_WIDTH - PANEL_PADDING * 2, 18)
        self._tax_slider.value = eco.tax_rate
        self._tax_slider.draw(surf)
        y += 42

        # Resources
        draw_label(surf, "── Resources ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        for label, val, unit in [
            ("🌾 Food", eco.food, ""),
            ("🪵 Wood", eco.wood, ""),
            ("🪨 Stone", eco.stone, ""),
        ]:
            draw_label(surf, f"{label}: {val:.0f} {unit}", x, y, C_UI_TEXT, 11)
            y += 14

        y += 10
        draw_label(surf, "── Market ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        bw = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 4) // 2
        for i, (res, price) in enumerate([("Food $5", 5), ("Wood $8", 8), ("Stone $10", 10)]):
            by = y + i * 30
            rb = pygame.Rect(x, by, bw, 22)
            rs = pygame.Rect(x + bw + 4, by, bw, 22)
            hover_b = rb.collidepoint(pygame.mouse.get_pos())
            hover_s = rs.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, rb, f"Buy {res}", False, hover_b,
                        color=(30, 70, 30), size=10)
            draw_button(surf, rs, f"Sell", False, hover_s,
                        color=(70, 30, 30), size=10)
        y += 100

    # ── STATS mode ────────────────────────────────────────────────────────────

    def _draw_stats(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        draw_label(surf, "📊 Statistics", x, y, C_UI_ACCENT, 14)
        y += 24
        bm = game.building_manager
        cm = game.citizen_manager
        eco = game.economy

        for section, rows in [
            ("Population", [
                (f"Citizens: {cm.count}", C_UI_TEXT),
                (f"Housing: {bm.total_housing()}", C_UI_TEXT),
                (f"Jobs: {bm.total_jobs()}", C_UI_TEXT),
                (f"Avg Happiness: {cm.average_happiness:.0%}", C_UI_SUCCESS),
            ]),
            ("Economy", [
                (f"Treasury: ${eco.money:,.0f}", C_UI_SUCCESS if eco.money >= 0 else C_UI_DANGER),
                (f"Daily Income: ${eco.day_income:,.0f}", C_UI_TEXT),
                (f"Daily Expenses: ${eco.day_expenses:,.0f}", C_UI_TEXT),
                (f"Tax Rate: {eco.tax_rate:.0%}", C_UI_TEXT),
            ]),
            ("Resources", [
                (f"Food: {eco.food:.0f}  (prod {bm.total_food_production():.0f}/day)", C_UI_TEXT),
                (f"Wood: {eco.wood:.0f}", C_UI_TEXT),
                (f"Stone: {eco.stone:.0f}", C_UI_TEXT),
            ]),
            ("Buildings", [
                (f"Total: {len(list(bm.all_buildings()))}", C_UI_TEXT),
                (f"Houses: {len(bm.buildings_of_type('house'))}", C_UI_TEXT),
                (f"Farms: {len(bm.buildings_of_type('farm'))}", C_UI_TEXT),
                (f"Roads: {len(bm.buildings_of_type('road'))}", C_UI_TEXT),
            ]),
        ]:
            draw_label(surf, f"── {section} ──", x, y, C_UI_TEXT_DIM, 10)
            y += 14
            for txt, col in rows:
                draw_label(surf, txt, x + 4, y, col, 11)
                y += 13
            y += 8

    # ── ENVIRONMENT mode ──────────────────────────────────────────────────────

    def _draw_environment(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        draw_label(surf, "🌤 Environment", x, y, C_UI_ACCENT, 14)
        y += 24
        tm = game.time_manager
        env = game.environment
        draw_label(surf, f"Time: {tm.time_string}", x, y, C_UI_TEXT, 12)
        y += 16
        draw_label(surf, f"Season: {tm.season.capitalize()}", x, y, C_UI_TEXT, 12)
        y += 16
        draw_label(surf, f"Weather: {env.current_weather.replace('_',' ').title()}", x, y, C_UI_TEXT, 12)
        y += 24

        # Weather buttons
        draw_label(surf, "── Set Weather ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        weather_types = ["clear", "cloudy", "rain", "heavy_rain", "snow", "storm", "fog"]
        bw = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 4) // 2
        for i, wt in enumerate(weather_types):
            col_i = i % 2
            row_i = i // 2
            r = pygame.Rect(x + col_i * (bw + 4), y + row_i * 28, bw, 22)
            hover = r.collidepoint(pygame.mouse.get_pos())
            active = env.current_weather == wt
            draw_button(surf, r, wt.replace("_", " ").title(), active, hover, size=10)
        y += (len(weather_types) // 2 + 1) * 28 + 8

        # Season buttons
        draw_label(surf, "── Set Season ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        seasons = ["spring", "summer", "autumn", "winter"]
        bw2 = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 6) // 4
        for i, s in enumerate(seasons):
            r = pygame.Rect(x + i * (bw2 + 2), y, bw2, 22)
            hover = r.collidepoint(pygame.mouse.get_pos())
            active = tm.season == s
            draw_button(surf, r, s[:3].capitalize(), active, hover, size=9)
        y += 30

        # Time controls
        draw_label(surf, "── Adjust Hour ──", x, y, C_UI_TEXT_DIM, 10)
        y += 14
        bw3 = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 4) // 2
        r_minus = pygame.Rect(x, y, bw3, 24)
        r_plus  = pygame.Rect(x + bw3 + 4, y, bw3, 24)
        draw_button(surf, r_minus, "◀ -1h", False, r_minus.collidepoint(pygame.mouse.get_pos()), size=10)
        draw_button(surf, r_plus,  "+1h ▶", False, r_plus.collidepoint(pygame.mouse.get_pos()), size=10)

    # ── GOD MODE ─────────────────────────────────────────────────────────────

    def _draw_godmode(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        draw_label(surf, "⚡ God Mode", x, y, C_UI_ACCENT2, 14)
        y += 22
        draw_label(surf, "Direct intervention tools:", x, y, C_UI_TEXT_DIM, 10)
        y += 18
        bw = SIDEBAR_WIDTH - PANEL_PADDING * 2
        for label, action, col in _GOD_ACTIONS:
            r = pygame.Rect(x, y, bw, 26)
            if r.bottom > _TOP + _H - 4:
                break
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, label, False, hover, color=col, size=11)
            y += 29

    # ── SETTINGS mode ────────────────────────────────────────────────────────

    def _draw_settings(self, surf: pygame.Surface, game: "Game"):
        x, y = _LEFT + PANEL_PADDING, _TOP + PANEL_PADDING
        draw_label(surf, "⚙ Settings", x, y, C_UI_ACCENT, 14)
        y += 22
        draw_label(surf, "── Desktop Integration ──", x, y, C_UI_TEXT_DIM, 10)
        y += 16
        bw = SIDEBAR_WIDTH - PANEL_PADDING * 2
        for label, attr in [
            ("🔝 Always On Top", "desktop_always_on_top"),
            ("🖼 Wallpaper Mode", "desktop_wallpaper_mode"),
            ("👁 Click-Through", "desktop_click_through"),
        ]:
            val = getattr(game, attr, False)
            r = pygame.Rect(x, y, bw, 24)
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, f"{'✓ ' if val else ''}{label}", val, hover, size=10)
            y += 28

        y += 10
        draw_label(surf, "── Save / Load ──", x, y, C_UI_TEXT_DIM, 10)
        y += 16
        for label in ["💾 Save Game", "📂 Load Game", "🔄 New Game"]:
            r = pygame.Rect(x, y, bw, 26)
            hover = r.collidepoint(pygame.mouse.get_pos())
            draw_button(surf, r, label, False, hover, size=11)
            y += 30

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event, game: "Game", mode: str) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # scroll up
            self._scroll_y = max(0, self._scroll_y - 20)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # scroll down
            self._scroll_y += 20
            return True

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            # Slider needs motion events
            if mode == "economy" and self._tax_slider.handle_event(event):
                game.economy.tax_rate = self._tax_slider.value
                return True
            return False

        pos = event.pos
        if not (pos[0] >= _LEFT):
            return False  # click not in sidebar

        y = _TOP + PANEL_PADDING

        if mode == "build":
            return self._handle_build_click(pos, game, y)
        if mode == "citizens":
            return self._handle_citizens_click(pos, game)
        if mode == "economy":
            return self._handle_economy_click(pos, game)
        if mode == "environment":
            return self._handle_environment_click(pos, game)
        if mode == "godmode":
            return self._handle_godmode_click(pos, game)
        if mode == "settings":
            return self._handle_settings_click(pos, game)

        return False

    def _handle_build_click(self, pos, game, start_y):
        x = _LEFT + PANEL_PADDING
        y = start_y
        cats = list(CATEGORIES)
        tab_w = (SIDEBAR_WIDTH - PANEL_PADDING * 2) // len(cats)
        # Category tabs
        for i, cat in enumerate(cats):
            r = pygame.Rect(x + i * tab_w, y, tab_w, 24)
            if r.collidepoint(pos):
                self._cat_index = i
                self._scroll_y = 0
                return True
        y += 30

        # Building list
        cat = cats[self._cat_index]
        for btype, bdef in BUILDING_CATALOGUE.items():
            if bdef.category != cat:
                continue
            r = pygame.Rect(x, y - self._scroll_y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 54)
            if r.collidepoint(pos):
                if game.selected_building_type == btype:
                    game.selected_building_type = None
                else:
                    game.selected_building_type = btype
                return True
            y += 58

        # Demolish
        if game.selected_tile:
            col, row = game.selected_tile
            t = game.grid.get(col, row)
            if t and t.building_id:
                r = pygame.Rect(x, y - self._scroll_y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 28)
                if r.collidepoint(pos):
                    game.building_manager.demolish(t.building_id, game.grid, game.economy)
                    game.selected_tile = None
                    game.show_notification("Building demolished", game.hud._notifs)
                    return True

        # Cancel
        if game.selected_building_type:
            r = pygame.Rect(x, _TOP + _H - 36, SIDEBAR_WIDTH - PANEL_PADDING * 2, 28)
            if r.collidepoint(pos):
                game.selected_building_type = None
                return True
        return False

    def _handle_citizens_click(self, pos, game):
        x = _LEFT + PANEL_PADDING
        y = _TOP + PANEL_PADDING + 22 + 16 + 14 + 16
        sc = getattr(game, 'selected_citizen', None)
        if sc:
            y += 134
        y += 14
        for cit in list(game.citizen_manager.all_citizens())[:12]:
            r = pygame.Rect(x, y, SIDEBAR_WIDTH - PANEL_PADDING * 2, 22)
            if r.collidepoint(pos):
                if game.selected_citizen and game.selected_citizen.id == cit.id:
                    game.selected_citizen = None
                else:
                    game.selected_citizen = cit
                return True
            y += 24
        return False

    def _handle_economy_click(self, pos, game):
        # Tax slider handled in handle_event via motion
        return False

    def _handle_environment_click(self, pos, game):
        x = _LEFT + PANEL_PADDING
        y = _TOP + PANEL_PADDING + 24 + 16 + 16 + 16 + 24 + 14
        weather_types = ["clear", "cloudy", "rain", "heavy_rain", "snow", "storm", "fog"]
        bw = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 4) // 2
        for i, wt in enumerate(weather_types):
            col_i = i % 2
            row_i = i // 2
            r = pygame.Rect(x + col_i * (bw + 4), y + row_i * 28, bw, 22)
            if r.collidepoint(pos):
                game.environment.set_weather(wt)
                return True
        y += (len(weather_types) // 2 + 1) * 28 + 8 + 14
        seasons = ["spring", "summer", "autumn", "winter"]
        bw2 = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 6) // 4
        for i, s in enumerate(seasons):
            r = pygame.Rect(x + i * (bw2 + 2), y, bw2, 22)
            if r.collidepoint(pos):
                game.time_manager.season_index = i
                return True
        y += 30 + 14
        bw3 = (SIDEBAR_WIDTH - PANEL_PADDING * 2 - 4) // 2
        if pygame.Rect(x, y, bw3, 24).collidepoint(pos):
            game.time_manager.hour = (game.time_manager.hour - 1) % 24
            return True
        if pygame.Rect(x + bw3 + 4, y, bw3, 24).collidepoint(pos):
            game.time_manager.hour = (game.time_manager.hour + 1) % 24
            return True
        return False

    def _handle_godmode_click(self, pos, game):
        x = _LEFT + PANEL_PADDING
        y = _TOP + PANEL_PADDING + 22 + 18
        bw = SIDEBAR_WIDTH - PANEL_PADDING * 2
        for label, action, col in _GOD_ACTIONS:
            r = pygame.Rect(x, y, bw, 26)
            if r.collidepoint(pos):
                self._execute_god_action(action, game)
                return True
            y += 29
        return False

    def _execute_god_action(self, action: str, game: "Game"):
        if action == "spawn5":
            for _ in range(5):
                tiles = [t for t in game.grid.all_tiles() if t.walkable and t.building_id is None]
                if tiles:
                    import random
                    t = random.choice(tiles)
                    game.citizen_manager.spawn(game, t.col, t.row)
            game.show_notification("Spawned 5 citizens!", color=game.hud._notifs)
        elif action == "add_money":
            game.economy.add_money(1000)
            game.show_notification("+$1000 added", color=None)
        elif action == "add_food":
            game.economy.food += 50
            game.show_notification("+50 Food")
        elif action == "add_wood":
            game.economy.wood += 50
            game.show_notification("+50 Wood")
        elif action == "add_stone":
            game.economy.stone += 50
            game.show_notification("+50 Stone")
        elif action == "happy_all":
            game.citizen_manager.set_all_happiness(1.0)
            game.show_notification("All citizens maximally happy!")
        elif action == "feed_all":
            for c in game.citizen_manager.all_citizens():
                c.hunger = 1.0
            game.show_notification("All citizens fed!")
        elif action == "energize_all":
            for c in game.citizen_manager.all_citizens():
                c.energy = 1.0
            game.show_notification("All citizens energised!")
        elif action == "build_all":
            for b in game.building_manager.all_buildings():
                if b.under_construction:
                    b.instant_build()
            game.show_notification("All buildings completed!")
        elif action == "meteor":
            game.trigger_meteor_event()
        elif action == "sunrise":
            game.time_manager.hour = 7
            game.time_manager.minute = 0
            game.show_notification("Set to sunrise (07:00)")
        elif action == "sunset":
            game.time_manager.hour = 19
            game.time_manager.minute = 0
            game.show_notification("Set to sunset (19:00)")

    def _handle_settings_click(self, pos, game):
        x = _LEFT + PANEL_PADDING
        y = _TOP + PANEL_PADDING + 22 + 16
        bw = SIDEBAR_WIDTH - PANEL_PADDING * 2
        for label, attr in [
            ("Always On Top", "desktop_always_on_top"),
            ("Wallpaper Mode", "desktop_wallpaper_mode"),
            ("Click-Through", "desktop_click_through"),
        ]:
            r = pygame.Rect(x, y, bw, 24)
            if r.collidepoint(pos):
                setattr(game, attr, not getattr(game, attr, False))
                game.apply_desktop_settings()
                return True
            y += 28
        y += 10 + 16
        for label, action in [("Save", "save"), ("Load", "load"), ("New", "new")]:
            r = pygame.Rect(x, y, bw, 26)
            if r.collidepoint(pos):
                if action == "save":
                    game.save_manager.save(game)
                    game.show_notification("Game saved!")
                elif action == "load":
                    game.save_manager.load(game)
                    game.show_notification("Game loaded!")
                elif action == "new":
                    game.new_game()
                    game.show_notification("New game started!")
                return True
            y += 30
        return False

    def in_sidebar(self, pos: tuple[int, int]) -> bool:
        return pos[0] >= _LEFT
