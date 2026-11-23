"""
TerraDesk – UI Base Helpers
Shared drawing primitives used by toolbar, sidebar and HUD.
"""
from __future__ import annotations
import pygame
from src.core.constants import (
    C_UI_PANEL, C_UI_BORDER, C_UI_BUTTON, C_UI_BUTTON_HOV, C_UI_BUTTON_ACT,
    C_UI_TEXT, C_UI_TEXT_DIM, C_UI_ACCENT, C_UI_SUCCESS, C_UI_DANGER,
    C_UI_WARNING, PANEL_PADDING,
)

# ── Fonts (lazy init after pygame.init) ─────────────────────────────────────
_fonts: dict[int, pygame.font.Font] = {}


def font(size: int = 14) -> pygame.font.Font:
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("segoeui,arial,sans-serif", size)
    return _fonts[size]


# ── Primitive helpers ────────────────────────────────────────────────────────

def draw_panel(surf: pygame.Surface, rect: pygame.Rect,
               color=C_UI_PANEL, border=C_UI_BORDER, radius: int = 4):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    pygame.draw.rect(surf, border, rect, 1, border_radius=radius)


def draw_label(surf: pygame.Surface, text: str, x: int, y: int,
               color=C_UI_TEXT, size: int = 13, align: str = "left"):
    s = font(size).render(text, True, color)
    if align == "center":
        x -= s.get_width() // 2
    elif align == "right":
        x -= s.get_width()
    surf.blit(s, (x, y))
    return s.get_width()


def draw_button(surf: pygame.Surface, rect: pygame.Rect, text: str,
                active: bool = False, hover: bool = False,
                color=None, text_color=C_UI_TEXT, size: int = 12) -> None:
    bg = color or (C_UI_BUTTON_ACT if active else C_UI_BUTTON_HOV if hover else C_UI_BUTTON)
    pygame.draw.rect(surf, bg, rect, border_radius=3)
    pygame.draw.rect(surf, C_UI_BORDER, rect, 1, border_radius=3)
    s = font(size).render(text, True, text_color)
    surf.blit(s, (rect.centerx - s.get_width() // 2,
                  rect.centery - s.get_height() // 2))


def draw_progress_bar(surf: pygame.Surface, rect: pygame.Rect,
                      value: float, color=C_UI_SUCCESS,
                      bg=(40, 42, 54), border=C_UI_BORDER):
    """value: 0.0 … 1.0"""
    pygame.draw.rect(surf, bg, rect, border_radius=2)
    if value > 0:
        filled = pygame.Rect(rect.x, rect.y, int(rect.w * value), rect.h)
        pygame.draw.rect(surf, color, filled, border_radius=2)
    pygame.draw.rect(surf, border, rect, 1, border_radius=2)


# ── Button widget ─────────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect: pygame.Rect, text: str,
                 color=None, text_color=C_UI_TEXT, size: int = 12,
                 tooltip: str = ""):
        self.rect = rect
        self.text = text
        self.color = color
        self.text_color = text_color
        self.size = size
        self.tooltip = tooltip
        self.active = False
        self.enabled = True

    def draw(self, surf: pygame.Surface, mouse_pos=None):
        hover = bool(mouse_pos and self.rect.collidepoint(mouse_pos))
        col = self.color or (C_UI_BUTTON_ACT if self.active else
                             C_UI_BUTTON_HOV if hover else C_UI_BUTTON)
        if not self.enabled:
            col = tuple(max(0, c - 30) for c in col)
        draw_button(surf, self.rect, self.text, self.active, hover, col,
                    self.text_color, self.size)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (self.enabled and
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Slider widget ─────────────────────────────────────────────────────────────

class Slider:
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float,
                 value: float, label: str = ""):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self._dragging = False

    @property
    def _knob_x(self) -> int:
        t = (self.value - self.min_val) / max(0.001, self.max_val - self.min_val)
        return self.rect.x + int(t * self.rect.w)

    def draw(self, surf: pygame.Surface):
        # Track
        track = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.w, 4)
        pygame.draw.rect(surf, C_UI_BORDER, track, border_radius=2)
        filled = pygame.Rect(track.x, track.y, self._knob_x - track.x, 4)
        pygame.draw.rect(surf, C_UI_ACCENT, filled, border_radius=2)
        # Knob
        pygame.draw.circle(surf, C_UI_ACCENT, (self._knob_x, self.rect.centery), 6)
        # Label + value
        if self.label:
            draw_label(surf, f"{self.label}: {self.value:.0%}", self.rect.x,
                       self.rect.y - 15, C_UI_TEXT_DIM, 11)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self._knob_x
            if abs(event.pos[0] - kx) <= 10 and self.rect.collidepoint(event.pos):
                self._dragging = True
                return True
        if event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False
        if event.type == pygame.MOUSEMOTION and self._dragging:
            t = max(0.0, min(1.0, (event.pos[0] - self.rect.x) / self.rect.w))
            self.value = self.min_val + t * (self.max_val - self.min_val)
            return True
        return False


# ── Scroll panel ─────────────────────────────────────────────────────────────

class ScrollPanel:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.scroll_y: int = 0
        self._content_h: int = 0

    def begin(self, surf: pygame.Surface):
        self._surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        self._surf.fill((0, 0, 0, 0))
        return self._surf

    def end(self, surf: pygame.Surface):
        surf.blit(self._surf, (self.rect.x, self.rect.y))

    def scroll(self, dy: int):
        self.scroll_y = max(0, min(
            max(0, self._content_h - self.rect.h),
            self.scroll_y - dy * 20
        ))
