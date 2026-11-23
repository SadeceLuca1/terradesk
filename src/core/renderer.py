"""
TerraDesk – Isometric Renderer
Draws the entire world onto the view surface using procedural pygame shapes.
Render order: terrain → roads → buildings → citizens → effects.
"""

from __future__ import annotations
import pygame
import math
from typing import TYPE_CHECKING
from src.core.constants import *

if TYPE_CHECKING:
    from src.core.game import Game
    from src.core.camera import Camera
    from src.core.grid import Tile


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_col(c1, c2, t):
    return tuple(max(0, min(255, int(c1[i] + (c2[i] - c1[i]) * t))) for i in range(3))


class Renderer:
    def __init__(self, screen: pygame.Surface, camera: "Camera"):
        self.screen = screen
        self.camera = camera
        self._view_surf: pygame.Surface | None = None
        self._anim_tick = 0

    # ------------------------------------------------------------------ main draw

    def draw(self, game: "Game"):
        cam = self.camera
        vw, vh = cam.view_w, cam.view_h

        # Reuse/resize view surface
        if self._view_surf is None or self._view_surf.get_size() != (vw, vh):
            self._view_surf = pygame.Surface((vw, vh))

        surf = self._view_surf
        tm = game.time_manager
        self._anim_tick = game.time_manager.tick

        # Sky fill
        surf.fill(tm.sky_color)

        # Draw tiles sorted by isometric depth (col + row ascending)
        grid = game.grid
        z = cam.zoom
        hw = int(TILE_HALF_W * z)
        hh = int(TILE_HALF_H * z)

        for tile in self._visible_tiles(game):
            self._draw_tile(surf, tile, cam, tm, game, hw, hh)

        # Roads (second pass for road markings)
        for tile in self._visible_tiles(game):
            if tile.road:
                self._draw_road_top(surf, tile, cam, hw, hh)

        # Buildings
        bm = game.building_manager
        drawn_bids = set()
        for tile in self._visible_tiles(game):
            bid = tile.building_id
            if bid and bid not in drawn_bids:
                b = bm.get(bid)
                if b:
                    self._draw_building(surf, b, cam, tm, hw, hh)
                    drawn_bids.add(bid)

        # Citizens
        for cit in game.citizen_manager.all_citizens():
            if cam.tile_visible(cit.x, cit.y, 2):
                self._draw_citizen(surf, cit, cam, tm, hw, hh, game)

        # Night overlay
        if tm.darkness > 0.05:
            dark = pygame.Surface((vw, vh), pygame.SRCALPHA)
            alpha = int(tm.darkness * 160)
            dark.fill((0, 5, 20, alpha))
            surf.blit(dark, (0, 0))

        # Environment (rain, snow, etc.)
        game.environment.draw(surf, cam, game)

        # Blit view to screen
        self.screen.blit(surf, (0, TOOLBAR_HEIGHT))

    # ------------------------------------------------------------------ tile iteration

    def _visible_tiles(self, game: "Game"):
        """Yield tiles in painter's order (back to front = ascending col+row)."""
        cam = self.camera
        # Sample corners to find tile range
        corners = [
            cam.screen_to_tile(0, 0),
            cam.screen_to_tile(cam.view_w, 0),
            cam.screen_to_tile(0, cam.view_h),
            cam.screen_to_tile(cam.view_w, cam.view_h),
        ]
        min_sum = min(c + r for c, r in corners) - 2
        max_sum = max(c + r for c, r in corners) + 2
        min_col = max(0, min(c for c, r in corners) - 2)
        max_col = min(game.grid.cols - 1, max(c for c, r in corners) + 2)

        for diag in range(min_sum, max_sum + 1):
            for col in range(min_col, max_col + 1):
                row = diag - col
                if 0 <= row < game.grid.rows:
                    t = game.grid.get(col, row)
                    if t:
                        yield t

    # ------------------------------------------------------------------ terrain tile

    def _draw_tile(self, surf, tile: "Tile", cam, tm, game, hw, hh):
        cx, cy = cam.world_to_screen(tile.col, tile.row)
        cx, cy = int(cx), int(cy)
        z = cam.zoom
        depth = max(0, min(1, int(hh * 0.6)))  # sidewall thickness (px)

        t = tile.terrain
        season = tm.season

        # Pick colours based on terrain + season
        if t == 'water':
            wave = 0.5 + 0.5 * math.sin(self._anim_tick * 0.05 + tile.col * 0.3 + tile.row * 0.2)
            top  = _lerp_col(C_WATER_DARK, C_WATER_LIGHT, wave * 0.4)
            side = C_WATER_DARK
        elif t == 'grass':
            if season == 'winter':
                top, side = C_SNOW_LIGHT, C_SNOW_DARK
            elif season == 'autumn':
                top  = _lerp_col(C_GRASS_MID, (160, 110, 40), 0.5)
                side = _lerp_col(C_GRASS_DARK, (110, 75, 25), 0.5)
            elif season == 'summer':
                top, side = C_GRASS_MID, C_GRASS_DARK
            else:  # spring
                top, side = C_GRASS_LIGHT, C_GRASS_MID
        elif t == 'dirt':
            top, side = C_DIRT, C_DIRT_DARK
        elif t == 'sand':
            top, side = C_SAND, C_SAND_DARK
        elif t == 'rock':
            top, side = C_ROCK, C_ROCK_DARK
        else:
            top, side = C_GRASS_MID, C_GRASS_DARK

        # Hover highlight
        mx, my = pygame.mouse.get_pos()
        hcol, hrow = cam.screen_to_tile(mx, my - TOOLBAR_HEIGHT)
        if hcol == tile.col and hrow == tile.row:
            top = _lerp_col(top, (255, 255, 255), 0.12)

        # Selected tile highlight
        if hasattr(game, 'selected_tile') and game.selected_tile == (tile.col, tile.row):
            top = _lerp_col(top, C_UI_ACCENT, 0.3)

        # Diamond (top face)
        pts_top = [
            (cx,      cy - hh),
            (cx + hw, cy),
            (cx,      cy + hh),
            (cx - hw, cy),
        ]
        pygame.draw.polygon(surf, top, pts_top)

        # Left face (depth)
        if depth > 0 and t != 'water':
            pts_left = [
                (cx - hw, cy),
                (cx,      cy + hh),
                (cx,      cy + hh + depth),
                (cx - hw, cy + depth),
            ]
            pygame.draw.polygon(surf, side, pts_left)
            # Right face
            pts_right = [
                (cx,      cy + hh),
                (cx + hw, cy),
                (cx + hw, cy + depth),
                (cx,      cy + hh + depth),
            ]
            darker = _lerp_col(side, (0, 0, 0), 0.2)
            pygame.draw.polygon(surf, darker, pts_right)

        # Thin outline
        if cam.zoom > 0.6:
            pygame.draw.polygon(surf, (0, 0, 0), pts_top, 1)

        # Water shimmer
        if t == 'water' and cam.zoom > 0.5:
            shine = int(wave * 80)
            sh_surf = pygame.Surface((hw * 2, hh * 2), pygame.SRCALPHA)
            pygame.draw.polygon(sh_surf, (255, 255, 255, shine),
                                [(hw, 0), (hw * 2, hh), (hw, hh * 2), (0, hh)])
            surf.blit(sh_surf, (cx - hw, cy - hh))

    # ------------------------------------------------------------------ road top

    def _draw_road_top(self, surf, tile, cam, hw, hh):
        cx, cy = cam.world_to_screen(tile.col, tile.row)
        cx, cy = int(cx), int(cy)
        pts = [
            (cx,      cy - hh // 2),
            (cx + hw // 2, cy),
            (cx,      cy + hh // 2),
            (cx - hw // 2, cy),
        ]
        pygame.draw.polygon(surf, C_PATH_TOP, pts)
        if cam.zoom > 0.7:
            pygame.draw.polygon(surf, C_PATH_SIDE, pts, 1)

    # ------------------------------------------------------------------ buildings

    def _draw_building(self, surf, b, cam, tm, hw, hh):
        cx, cy = cam.world_to_screen(b.col + (b.width - 1) / 2, b.row + (b.height - 1) / 2)
        cx, cy = int(cx), int(cy)
        z = cam.zoom
        btype = b.building_type

        # Under construction: show ghost + progress bar
        if b.under_construction:
            self._draw_construction(surf, b, cx, cy, hw, hh)
            return

        if btype == 'road':
            return  # drawn separately
        if btype == 'tree':
            self._draw_tree(surf, b, cx, cy, z, tm)
            return
        if btype == 'farm':
            self._draw_farm(surf, b, cx, cy, hw, hh, tm)
            return
        if btype == 'well':
            self._draw_well(surf, b, cx, cy, z, tm)
            return
        if btype == 'bridge':
            self._draw_bridge(surf, b, cx, cy, hw, hh)
            return

        # Generic house-like building
        self._draw_generic_building(surf, b, cx, cy, hw, hh, z, tm)

    def _draw_construction(self, surf, b, cx, cy, hw, hh):
        # Scaffolding ghost
        alpha = int(80 + 100 * b.construction_progress)
        pts = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
        s = pygame.Surface((hw * 2 + 4, hh * 4 + 4), pygame.SRCALPHA)
        poly = [(hw + 2, 2), (hw * 2 + 2, hh + 2), (hw + 2, hh * 2 + 2), (2, hh + 2)]
        pygame.draw.polygon(s, (200, 180, 100, alpha), poly)
        surf.blit(s, (cx - hw - 2, cy - hh - 2))
        # Progress bar
        bw = hw * 2
        bh = max(3, int(hh * 0.3))
        bar_x = cx - hw
        bar_y = cy - hh - bh - 4
        pygame.draw.rect(surf, (40, 40, 50), (bar_x, bar_y, bw, bh))
        pygame.draw.rect(surf, C_UI_WARNING,
                         (bar_x, bar_y, int(bw * b.construction_progress), bh))

    def _draw_generic_building(self, surf, b, cx, cy, hw, hh, z, tm):
        btype = b.building_type
        # Roof colour per type
        roof_map = {
            'house':      (C_ROOF_RED,    C_ROOF_RED_D),
            'market':     (C_ROOF_BLUE,   C_ROOF_BLUE_D),
            'school':     (C_ROOF_GREY,   C_ROOF_GREY_D),
            'hospital':   (C_ROOF_BLUE,   C_ROOF_BLUE_D),
            'church':     (C_ROOF_GREY,   C_ROOF_GREY_D),
            'tavern':     (C_ROOF_BROWN,  C_ROOF_BROWN_D),
            'mill':       (C_ROOF_BROWN,  C_ROOF_BROWN_D),
            'blacksmith': (C_ROOF_GREY,   C_ROOF_GREY_D),
            'warehouse':  (C_ROOF_BROWN,  C_ROOF_BROWN_D),
        }
        rc, rcd = roof_map.get(btype, (C_ROOF_RED, C_ROOF_RED_D))

        bw = int(hw * 0.9 * b.width)
        bh_tile = int(hh * 0.9 * b.height)
        wall_h = int(hh * 1.4)

        # Base/foundation
        base_pts = [
            (cx,       cy - bh_tile),
            (cx + bw,  cy),
            (cx,       cy + bh_tile),
            (cx - bw,  cy),
        ]
        pygame.draw.polygon(surf, C_GRASS_MID, base_pts)

        # Left wall
        wl = [
            (cx - bw, cy),
            (cx,      cy + bh_tile),
            (cx,      cy + bh_tile + wall_h),
            (cx - bw, cy + wall_h),
        ]
        pygame.draw.polygon(surf, C_WALL_MID, wl)

        # Right wall (darker)
        wr = [
            (cx,      cy + bh_tile),
            (cx + bw, cy),
            (cx + bw, cy + wall_h),
            (cx,      cy + bh_tile + wall_h),
        ]
        pygame.draw.polygon(surf, C_WALL_DARK, wr)

        # Roof (simple pitched)
        roof_pts = [
            (cx,          cy - bh_tile - wall_h),
            (cx + bw,     cy - wall_h),
            (cx,          cy + bh_tile - wall_h),
            (cx - bw,     cy - wall_h),
        ]
        pygame.draw.polygon(surf, rc, roof_pts)
        # Roof ridge (front face shade)
        ridge_pts = [
            (cx,      cy - bh_tile - wall_h),
            (cx - bw, cy - wall_h),
            (cx - bw, cy + wall_h),
            (cx,      cy + bh_tile - wall_h),
        ]
        pygame.draw.polygon(surf, rcd, ridge_pts)

        # Window
        win_x = cx - bw // 2 + 2
        win_y = cy + wall_h // 2
        win_w = max(4, int(bw * 0.3))
        win_h = max(3, int(wall_h * 0.35))
        win_color = C_WINDOW_GLOW if tm.window_light else C_WINDOW_DAY
        pygame.draw.rect(surf, win_color, (win_x, win_y - win_h, win_w, win_h))
        pygame.draw.rect(surf, (0, 0, 0), (win_x, win_y - win_h, win_w, win_h), 1)

        # Door
        door_x = cx + bw // 4
        door_y = cy + bh_tile // 2
        dw = max(4, int(bw * 0.25))
        dh = max(5, int(wall_h * 0.5))
        pygame.draw.rect(surf, C_DOOR, (door_x, door_y - dh + wall_h // 2, dw, dh))

        # Chimney (houses, tavern)
        if btype in ('house', 'tavern'):
            chx = cx + int(bw * 0.1)
            chy = cy - bh_tile - wall_h - int(hh * 0.6)
            cw = max(3, int(bw * 0.12))
            ch = int(hh * 0.6)
            pygame.draw.rect(surf, C_CHIMNEY, (chx, chy, cw, ch))
            # Smoke
            if self._anim_tick % 20 < 10:
                pygame.draw.circle(surf, (180, 180, 185), (chx + cw // 2, chy - 3), 2)

        # Outline
        if cam_zoom := 1.0:  # always draw outline
            pygame.draw.polygon(surf, (0, 0, 0), roof_pts, 1)
            pygame.draw.polygon(surf, (0, 0, 0), wl, 1)

    def _draw_tree(self, surf, b, cx, cy, z, tm):
        season = tm.season
        col_map = {
            'spring': C_TREE_SPRING,
            'summer': C_TREE_SUMMER,
            'autumn': C_TREE_AUTUMN,
            'winter': C_TREE_WINTER,
        }
        tc = col_map.get(season, C_TREE_SUMMER)
        sway = int(2 * math.sin(self._anim_tick * 0.04 + b.col * 0.5))
        trunk_h = max(6, int(16 * z))
        trunk_w = max(2, int(4 * z))
        crown_r = max(5, int(12 * z))
        # Trunk
        pygame.draw.rect(surf, C_TREE_TRUNK,
                         (cx - trunk_w // 2, cy - trunk_h, trunk_w, trunk_h))
        # Crown (layered circles)
        pygame.draw.circle(surf, _lerp_col(tc, (0,0,0), 0.2),
                           (cx + sway, cy - trunk_h - crown_r + 3), crown_r)
        pygame.draw.circle(surf, tc,
                           (cx + sway, cy - trunk_h - crown_r), crown_r)
        pygame.draw.circle(surf, _lerp_col(tc, (255,255,255), 0.15),
                           (cx + sway - 2, cy - trunk_h - crown_r - 2), crown_r // 2)

    def _draw_farm(self, surf, b, cx, cy, hw, hh, tm):
        z = self.camera.zoom
        # Ploughed field base
        field_pts = [
            (cx,      cy - hh),
            (cx + hw, cy),
            (cx,      cy + hh),
            (cx - hw, cy),
        ]
        field_col = C_FIELD_BROWN
        pygame.draw.polygon(surf, field_col, field_pts)

        # Crop rows
        season = tm.season
        crop_col = C_CROP_YELLOW if season in ('summer', 'autumn') else C_CROP_GREEN
        for row_i in range(3):
            for col_i in range(3):
                fx = cx - hw // 2 + col_i * (hw // 3)
                fy = cy - hh // 4 + row_i * (hh // 3)
                pygame.draw.rect(surf, crop_col, (fx, fy, max(2, int(4 * z)), max(5, int(8 * z))))

        # Small barn structure
        barn_x = cx - hw // 4
        barn_y = cy - hh
        bw2 = int(hw * 0.4)
        bh2 = int(hh * 0.6)
        pygame.draw.rect(surf, C_WALL_MID, (barn_x, barn_y - bh2, bw2, bh2))
        # Roof triangle
        pts = [(barn_x - 2, barn_y - bh2),
               (barn_x + bw2 // 2, barn_y - bh2 - bh2 // 2),
               (barn_x + bw2 + 2, barn_y - bh2)]
        pygame.draw.polygon(surf, C_ROOF_RED, pts)

    def _draw_well(self, surf, b, cx, cy, z, tm):
        r = max(5, int(8 * z))
        h = max(6, int(10 * z))
        pygame.draw.circle(surf, C_ROCK, (cx, cy), r)
        pygame.draw.circle(surf, C_WATER_LIGHT, (cx, cy), max(2, r - 2))
        # Posts
        pygame.draw.line(surf, C_ROOF_BROWN, (cx - r, cy - 2), (cx - r, cy - h - 4), max(2, int(2*z)))
        pygame.draw.line(surf, C_ROOF_BROWN, (cx + r, cy - 2), (cx + r, cy - h - 4), max(2, int(2*z)))
        # Roof beam
        pygame.draw.line(surf, C_ROOF_BROWN_D, (cx - r - 2, cy - h - 4), (cx + r + 2, cy - h - 4), max(2, int(2*z)))
        # Bucket
        pygame.draw.circle(surf, C_DIRT, (cx, cy - h), max(2, int(3*z)))

    def _draw_bridge(self, surf, b, cx, cy, hw, hh):
        z = self.camera.zoom
        pts = [
            (cx,      cy - hh // 2),
            (cx + hw, cy),
            (cx,      cy + hh // 2),
            (cx - hw, cy),
        ]
        pygame.draw.polygon(surf, (160, 130, 90), pts)
        # Planks
        for i in range(5):
            t_frac = i / 5
            px1 = int(cx - hw + (cx - hw + hw * 2) * t_frac)
            px2 = int(cx - hw + (cx - hw + hw * 2) * (t_frac + 0.18))
            mid_y = cy + int((hh // 2) * (0.5 - abs(t_frac - 0.5) * 2) * 0.3)
            pygame.draw.line(surf, (130, 100, 60), (px1, mid_y - 2), (px2, mid_y + 2),
                             max(2, int(2 * z)))

    # ------------------------------------------------------------------ citizens

    def _draw_citizen(self, surf, cit, cam, tm, hw, hh, game):
        z = cam.zoom
        sx, sy = cam.world_to_screen(cit.x, cit.y)
        sx, sy = int(sx), int(sy)

        body_w = max(3, int(5 * z))
        body_h = max(5, int(9 * z))
        head_r = max(2, int(3 * z))

        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0),
                            (sx - body_w, sy - 1, body_w * 2, max(2, int(3*z))), 1)

        # Legs (walk animation)
        walk = abs(math.sin(game.time_manager.tick * 0.15 + cit.id)) if cit.state not in ('sleeping', 'idle') else 0
        leg_offset = int(walk * 2)
        pygame.draw.line(surf, cit.pants_color,
                         (sx - 1, sy), (sx - 2, sy + max(3, int(4*z)) + leg_offset), max(1, int(z)))
        pygame.draw.line(surf, cit.pants_color,
                         (sx + 1, sy), (sx + 2, sy + max(3, int(4*z)) - leg_offset), max(1, int(z)))

        # Body
        pygame.draw.rect(surf, cit.shirt_color,
                         (sx - body_w, sy - body_h, body_w * 2, body_h))

        # Head
        pygame.draw.circle(surf, C_CITIZEN_SKIN, (sx, sy - body_h - head_r), head_r)
        # Hair
        pygame.draw.arc(surf, cit.hair_color,
                        pygame.Rect(sx - head_r, sy - body_h - head_r * 2,
                                    head_r * 2, head_r * 2),
                        0, math.pi, max(1, head_r // 2))

        # State indicator dot
        state_colors = {
            'working': C_UI_SUCCESS,
            'sleeping': C_UI_ACCENT,
            'socialising': C_UI_ACCENT2,
            'eating': C_UI_WARNING,
        }
        sc = state_colors.get(cit.state)
        if sc and z > 0.6:
            pygame.draw.circle(surf, sc, (sx + head_r + 1, sy - body_h - head_r * 2), 2)

        # Selection ring
        if hasattr(game, 'selected_citizen') and game.selected_citizen and game.selected_citizen.id == cit.id:
            pygame.draw.circle(surf, C_UI_ACCENT,
                               (sx, sy - body_h // 2), max(8, int(12 * z)), 2)
            # Name label above
            if z > 0.6:
                name_surf = pygame.font.SysFont(None, max(10, int(12 * z))).render(
                    cit.first_name, True, C_UI_TEXT)
                surf.blit(name_surf, (sx - name_surf.get_width() // 2,
                                      sy - body_h - head_r * 2 - name_surf.get_height() - 2))