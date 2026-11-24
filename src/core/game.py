"""
TerraDesk – Game
Central coordinator: initialises all subsystems and runs the main loop.
"""
from __future__ import annotations
import sys
import random
import pygame

from src.core.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TOOLBAR_HEIGHT, SIDEBAR_WIDTH, FPS_TARGET,
    AUTOSAVE_INTERVAL, C_UI_SUCCESS, C_UI_DANGER, C_UI_WARNING, C_UI_ACCENT,
    DESKTOP_ALWAYS_ON_TOP, DESKTOP_WALLPAPER_MODE, DESKTOP_CLICK_THROUGH,
)
from src.core.camera   import Camera
from src.core.grid     import Grid
from src.core.renderer import Renderer
from src.world.time_manager  import TimeManager
from src.world.environment   import Environment
from src.buildings.building_manager import BuildingManager
from src.citizens.citizen_manager   import CitizenManager
from src.economy.economy            import Economy
from src.ui.toolbar  import Toolbar
from src.ui.sidebar  import Sidebar
from src.ui.hud      import HUD
from src.save.save_manager import SaveManager


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # State
        self.mode: str = "build"
        self.running: bool = True
        self.selected_building_type: str | None = None
        self.selected_tile: tuple[int, int] | None = None
        self.selected_citizen = None

        # Desktop flags
        self.desktop_always_on_top: bool = DESKTOP_ALWAYS_ON_TOP
        self.desktop_wallpaper_mode: bool = DESKTOP_WALLPAPER_MODE
        self.desktop_click_through: bool = DESKTOP_CLICK_THROUGH

        # Subsystems
        self.camera          = Camera()
        self.grid            = Grid()
        self.time_manager    = TimeManager()
        self.environment     = Environment()
        self.building_manager = BuildingManager()
        self.citizen_manager  = CitizenManager()
        self.economy          = Economy()

        # UI
        self.renderer    = Renderer(screen, self.camera)
        self.toolbar     = Toolbar()
        self.sidebar     = Sidebar()
        self.hud         = HUD()
        self.save_manager = SaveManager()

        # Timers
        self._autosave_timer: float = 0.0
        self._clock = pygame.time.Clock()

        # Particle effects
        self._particles: list[dict] = []

        # Build starter village
        self._create_starter_village()

    # ── Starter village ───────────────────────────────────────────────────────

    def _create_starter_village(self):
        g = self.grid
        # Find a cluster of buildable tiles near centre
        cx, cy = g.cols // 2, g.rows // 2
        # Scan outward for buildable spots
        buildable = [(t.col, t.row) for t in g.all_tiles()
                     if t.buildable and
                     abs(t.col - cx) < 15 and abs(t.row - cy) < 15]
        if not buildable:
            buildable = [(t.col, t.row) for t in g.all_tiles() if t.buildable]

        placed = []

        def try_place(btype, w=1, h=1):
            random.shuffle(buildable)
            for c, r in buildable:
                ok = True
                for dc in range(w):
                    for dr in range(h):
                        t = g.get(c + dc, r + dr)
                        if not t or not t.buildable or t.building_id is not None:
                            ok = False
                            break
                if ok:
                    b = self.building_manager.place(btype, c, r, g, instant=True)
                    if b:
                        placed.append((c, r))
                        return c, r
            return None, None

        # Place initial buildings
        try_place("house")
        try_place("house")
        try_place("house")
        try_place("farm", 2, 2)
        try_place("well")

        # Roads between buildings
        road_spots = [(t.col, t.row) for t in g.all_tiles()
                      if t.buildable and t.building_id is None and
                      abs(t.col - cx) < 10 and abs(t.row - cy) < 10]
        for c, r in road_spots[:8]:
            self.building_manager.place("road", c, r, g, instant=True)

        # Trees around perimeter
        tree_spots = [(t.col, t.row) for t in g.all_tiles()
                      if t.buildable and t.building_id is None and
                      abs(t.col - cx) < 20 and abs(t.row - cy) < 20]
        for c, r in tree_spots[:12]:
            self.building_manager.place("tree", c, r, g, instant=True)

        # Spawn citizens
        walk_spots = [(t.col, t.row) for t in g.all_tiles()
                      if t.walkable and t.building_id is None]
        for _ in range(5):
            if walk_spots:
                c, r = random.choice(walk_spots)
                self.citizen_manager.spawn(self, c, r)

    # ── Main loop ──────────────────────────────────────────────────────────────

    def run(self):
        self.apply_desktop_settings()
        while self.running:
            dt = self._clock.tick(FPS_TARGET) / 1000.0
            dt = min(dt, 0.1)  # cap to avoid spiral of death
            self._handle_events()
            self._update(dt)
            self._draw()

    # ── Events ────────────────────────────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                self._handle_key(event)
            if event.type == pygame.MOUSEWHEEL:
                self._handle_viewport_event(event)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.toolbar.handle_event(event, self):
                    continue
                if self.sidebar.handle_event(event, self, self.mode):
                    continue
                self._handle_left_click(event)
            if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self.sidebar.handle_event(event, self, self.mode)
                self._handle_viewport_event(event)

    def _handle_key(self, event: pygame.event.Event):
        k = event.key
        if k == pygame.K_ESCAPE:
            self.selected_building_type = None
            self.selected_tile = None
            self.selected_citizen = None
        elif k == pygame.K_SPACE:
            self.time_manager.toggle_pause()
        elif k == pygame.K_F5:
            self.save_manager.save(self)
            self.show_notification("Game saved (F5)")
        elif k == pygame.K_F9:
            self.save_manager.load(self)
            self.show_notification("Game loaded (F9)")
        elif k == pygame.K_1:
            self.time_manager.set_speed(1)
        elif k == pygame.K_2:
            self.time_manager.set_speed(2)
        elif k == pygame.K_3:
            self.time_manager.set_speed(3)
        elif k == pygame.K_4:
            self.time_manager.set_speed(4)
        elif k == pygame.K_0:
            self.time_manager.set_speed(0)
        elif k == pygame.K_r:
            self.camera.reset()

    def _handle_viewport_event(self, event: pygame.event.Event):
        pos = pygame.mouse.get_pos()
        # Only handle if in viewport (not toolbar/sidebar)
        if pos[1] < TOOLBAR_HEIGHT or pos[0] >= WINDOW_WIDTH - SIDEBAR_WIDTH:
            return
        view_y = pos[1] - TOOLBAR_HEIGHT

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.camera.zoom_in(pos[0], view_y)
            else:
                self.camera.zoom_out(pos[0], view_y)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            self.camera.start_drag(pos[0], view_y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.camera.end_drag()
        elif event.type == pygame.MOUSEMOTION:
            self.camera.update_drag(pos[0], view_y)

    def _handle_left_click(self, event: pygame.event.Event):
        pos = event.pos
        if pos[1] < TOOLBAR_HEIGHT:
            return
        if pos[0] >= WINDOW_WIDTH - SIDEBAR_WIDTH:
            return

        view_y = pos[1] - TOOLBAR_HEIGHT
        col, row = self.camera.screen_to_tile(pos[0], view_y)

        # Try click citizen first
        cit = self.citizen_manager.citizen_near(pos[0], view_y, self.camera, 20)
        if cit:
            self.selected_citizen = cit
            self.selected_tile = None
            return

        # Build mode
        if self.mode == "build" and self.selected_building_type:
            self._try_place_building(col, row)
            return

        # Select tile
        t = self.grid.get(col, row)
        if t:
            self.selected_tile = (col, row)
            self.selected_citizen = None

    def _try_place_building(self, col: int, row: int):
        btype = self.selected_building_type
        from src.buildings.building_types import get_cost, get_building_def
        cost = get_cost(btype)
        bdef = get_building_def(btype)
        if not self.economy.can_afford(cost):
            self.show_notification(f"Not enough money! (${cost} needed)", C_UI_DANGER)
            return
        b = self.building_manager.place(btype, col, row, self.grid)
        if b:
            self.economy.spend(cost, f"built {btype}")
            self.show_notification(f"Building {bdef.name}… (${cost})", C_UI_SUCCESS)
        else:
            self.show_notification("Can't place here!", C_UI_WARNING)

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self, dt: float):
        keys = pygame.key.get_pressed()
        self.camera.update(dt, keys)
        self.time_manager.update(dt)
        self.environment.update(dt, self.time_manager,
                                self.screen.get_width(),
                                self.screen.get_height())
        self.building_manager.update(self.time_manager.tick)
        self.citizen_manager.update(dt, self)
        self.economy.update(self)
        self.hud.update(dt)

        # Autosave
        self._autosave_timer += dt
        if self._autosave_timer >= AUTOSAVE_INTERVAL:
            self._autosave_timer = 0.0
            self.save_manager.save(self, slot="autosave")

        # Particles
        self._update_particles(dt)

    def _update_particles(self, dt: float):
        self._particles = [p for p in self._particles if p['life'] > 0]
        for p in self._particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 200 * dt  # gravity
            p['life'] -= dt

    # ── Draw ─────────────────────────────────────────────────────────────────

    def _draw(self):
        self.screen.fill((10, 12, 18))
        self.renderer.draw(self)
        self.toolbar.draw(self.screen, self)
        self.sidebar.draw(self.screen, self, self.mode)
        self._draw_particles()
        self.hud.draw(self.screen, self)
        pygame.display.flip()

    def _draw_particles(self):
        for p in self._particles:
            alpha = max(0, int(255 * p['life'] / p['max_life']))
            r = max(1, int(p.get('radius', 3) * p['life'] / p['max_life']))
            col = p['color']
            pygame.draw.circle(self.screen, col, (int(p['x']), int(p['y'])), r)

    # ── Special effects ───────────────────────────────────────────────────────

    def trigger_meteor_event(self):
        """God mode: meteor strike on a random building."""
        buildings = list(self.building_manager.all_buildings())
        if not buildings:
            self.show_notification("No buildings to strike!", C_UI_WARNING)
            return
        b = random.choice(buildings)
        # Particle explosion
        sx, sy = self.camera.world_to_screen(b.col, b.row)
        for _ in range(60):
            self._particles.append({
                'x': sx, 'y': sy + TOOLBAR_HEIGHT,
                'vx': random.uniform(-200, 200),
                'vy': random.uniform(-400, -50),
                'color': random.choice([(255, 100, 20), (255, 200, 50), (200, 50, 20)]),
                'life': random.uniform(0.5, 1.5),
                'max_life': 1.5,
                'radius': random.randint(2, 6),
            })
        self.building_manager.demolish(b.id, self.grid, self.economy)
        self.show_notification("☄ METEOR STRIKE!", C_UI_DANGER)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def show_notification(self, text: str, color=None):
        from src.core.constants import C_UI_TEXT
        self.hud.add_notification(text, color or C_UI_TEXT)

    def apply_desktop_settings(self):
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()["window"]
            HWND_TOPMOST    = -1
            HWND_NOTOPMOST  = -2
            SWP_NOSIZE      = 0x0001
            SWP_NOMOVE      = 0x0002
            SWP_SHOWWINDOW  = 0x0040
            flags = SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
            insert_after = HWND_TOPMOST if self.desktop_always_on_top else HWND_NOTOPMOST
            ctypes.windll.user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, flags)
        except Exception:
            pass  # Non-Windows or no display

    def new_game(self):
        self.grid            = Grid()
        self.time_manager    = TimeManager()
        self.environment     = Environment()
        self.building_manager = BuildingManager()
        self.citizen_manager  = CitizenManager()
        self.economy          = Economy()
        self.selected_building_type = None
        self.selected_tile = None
        self.selected_citizen = None
        self._particles.clear()
        self.camera.reset()
        self._create_starter_village()
        self.renderer.camera = self.camera
