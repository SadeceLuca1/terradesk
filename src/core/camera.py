"""
TerraDesk – Isometric Camera
Handles pan, zoom and coordinate transforms between world-tile space
and screen (view-surface) space.

World space  : (col, row)  – grid tile coordinates, floats OK
Screen space : (px, py)    – pixels on the view surface (excludes toolbar)
"""

from __future__ import annotations
import pygame
from src.core.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_HEIGHT, SIDEBAR_WIDTH,
    TILE_HALF_W, TILE_HALF_H, CAMERA_PAN_SPEED,
    CAMERA_ZOOM_MIN, CAMERA_ZOOM_MAX, CAMERA_ZOOM_STEP,
    GRID_COLS, GRID_ROWS,
)


class Camera:
    def __init__(self):
        self.zoom: float = 1.0
        # Offset: world-origin position in screen pixels
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        # Drag state
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._drag_offset_x: float = 0.0
        self._drag_offset_y: float = 0.0
        self._is_dragging: bool = False
        self.reset()

    @property
    def view_w(self):
        return WINDOW_WIDTH - SIDEBAR_WIDTH

    @property
    def view_h(self):
        return WINDOW_HEIGHT - TOOLBAR_HEIGHT

    @property
    def view_rect(self):
        """Screen rect of the viewport (excluding toolbar + sidebar)."""
        return pygame.Rect(0, TOOLBAR_HEIGHT, self.view_w, self.view_h)

    # ------------------------------------------------------------------ reset

    def reset(self):
        """Centre the camera on the grid."""
        cx = GRID_COLS / 2
        cy = GRID_ROWS / 2
        sx, sy = self._iso(cx, cy, 1.0)
        self.offset_x = self.view_w / 2 - sx
        self.offset_y = self.view_h / 2 - sy
        self.zoom = 1.0

    # ------------------------------------------------------------------ update

    def update(self, dt: float, keys):
        spd = CAMERA_PAN_SPEED * dt / self.zoom
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.offset_x += spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.offset_x -= spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            self.offset_y += spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            self.offset_y -= spd

    # ------------------------------------------------------------------ zoom

    def zoom_in(self, px: int, py: int):
        self._zoom_at(px, py, self.zoom * (1 + CAMERA_ZOOM_STEP))

    def zoom_out(self, px: int, py: int):
        self._zoom_at(px, py, self.zoom * (1 - CAMERA_ZOOM_STEP))

    def _zoom_at(self, px: int, py: int, new_zoom: float):
        new_zoom = max(CAMERA_ZOOM_MIN, min(CAMERA_ZOOM_MAX, new_zoom))
        # Keep the tile under the cursor fixed
        wx = (px - self.offset_x) / (TILE_HALF_W * self.zoom)
        wy = (py - self.offset_y) / (TILE_HALF_H * self.zoom * 2)
        col = (wx + wy) / 2
        row = (wy - wx) / 2 + wy / 2  # recalculate
        # Recalculate via inverse
        col = (wx + wy) / 2
        row = wy - col

        self.zoom = new_zoom
        nx, ny = self._iso(col, row, new_zoom)
        self.offset_x = px - nx
        self.offset_y = py - ny

    # ------------------------------------------------------------------ drag

    def start_drag(self, px: int, py: int):
        self._is_dragging = True
        self._drag_start_x = px
        self._drag_start_y = py
        self._drag_offset_x = self.offset_x
        self._drag_offset_y = self.offset_y

    def update_drag(self, px: int, py: int):
        if self._is_dragging:
            self.offset_x = self._drag_offset_x + (px - self._drag_start_x)
            self.offset_y = self._drag_offset_y + (py - self._drag_start_y)

    def end_drag(self):
        self._is_dragging = False

    # ------------------------------------------------------------------ coordinate transforms

    @staticmethod
    def _iso(col: float, row: float, zoom: float):
        """World (col, row) → screen (px, py) at given zoom (no offset)."""
        px = (col - row) * TILE_HALF_W * zoom
        py = (col + row) * TILE_HALF_H * zoom
        return px, py

    def world_to_screen(self, col: float, row: float):
        """World tile → view-surface pixel (excludes toolbar offset)."""
        px, py = self._iso(col, row, self.zoom)
        return px + self.offset_x, py + self.offset_y

    def screen_to_tile(self, px: float, py: float):
        """View-surface pixel → nearest tile (col, row)."""
        # Undo offset
        rx = (px - self.offset_x) / (TILE_HALF_W * self.zoom)
        ry = (py - self.offset_y) / (TILE_HALF_H * self.zoom)
        col = int((rx + ry) / 2)
        row = int((ry - rx) / 2)
        return col, row

    def tile_visible(self, col: int, row: int, margin: int = 2) -> bool:
        """Quick cull: is this tile on screen?"""
        sx, sy = self.world_to_screen(col, row)
        hw = TILE_HALF_W * self.zoom
        hh = TILE_HALF_H * self.zoom
        return (-hw * margin < sx < self.view_w + hw * margin and
                -hh * margin < sy < self.view_h + hh * margin)