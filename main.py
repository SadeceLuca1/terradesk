"""
TerraDesk – Entry Point
Usage:
  python main.py              # Normal windowed mode
  python main.py --wallpaper  # Wallpaper mode (always on top, no taskbar)
  python main.py --windowed   # Force windowed (default)
  python main.py --test-engine  # Headless smoke-test (no window, CI-safe)
"""

import sys
import os

# Allow running from the project root with `python main.py`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _headless_test():
    """Smoke-test: init subsystems without opening a display window."""
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Import everything and do a brief sim cycle
    from src.core.constants import GRID_COLS, GRID_ROWS
    from src.core.grid import Grid
    from src.core.camera import Camera
    from src.world.time_manager import TimeManager
    from src.world.environment import Environment
    from src.buildings.building_manager import BuildingManager
    from src.citizens.citizen_manager import CitizenManager
    from src.economy.economy import Economy

    g = Grid(30, 30)
    cam = Camera()
    tm = TimeManager()
    env = Environment()
    bm = BuildingManager()
    cm = CitizenManager()
    eco = Economy()

    # Find buildable tiles
    buildable = [(t.col, t.row) for t in g.all_tiles() if t.buildable]
    assert buildable, "No buildable tiles on 30×30 grid"

    # Place buildings
    c0, r0 = buildable[0]
    h = bm.place("house", c0, r0, g, instant=True)
    assert h and h.is_complete, f"House placement failed at ({c0},{r0})"

    # Find 2×2 spot for farm
    farm = None
    for c, r in buildable:
        tiles = [g.get(c + dc, r + dr) for dc in range(2) for dr in range(2)]
        if all(t and t.buildable and t.building_id is None for t in tiles):
            farm = bm.place("farm", c, r, g, instant=True)
            if farm:
                break
    assert farm and farm.is_complete, "Farm placement failed"

    # Coordinate transforms
    sx, sy = cam.world_to_screen(15, 15)
    bc, br = cam.screen_to_tile(sx, sy)
    assert bc == 15 and br == 15, f"Round-trip failed: ({bc},{br})"

    # Economy
    eco.money = 500
    assert eco.can_afford(400)
    assert not eco.can_afford(600)
    eco.spend(100)
    assert eco.money == 400

    # Time
    tm.update(1.0)
    assert tm.tick > 0

    print("PASS: headless smoke-test")
    pygame.quit()
    return 0


def main():
    args = sys.argv[1:]

    if "--test-engine" in args:
        sys.exit(_headless_test())

    # Set up SDL for real display
    import os
    # Ensure audio doesn't crash in environments without audio
    os.environ.setdefault("SDL_AUDIODRIVER", "directsound")

    import pygame
    pygame.init()
    pygame.font.init()

    from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, DESKTOP_ALWAYS_ON_TOP

    flags = pygame.NOFRAME if "--wallpaper" in args else 0
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    pygame.display.set_caption("TerraDesk – Village Simulation")

    # App icon (simple coloured square if no icon file)
    try:
        icon = pygame.Surface((32, 32))
        icon.fill((80, 160, 80))
        pygame.draw.circle(icon, (60, 120, 60), (16, 16), 12)
        pygame.draw.circle(icon, (100, 200, 100), (14, 12), 7)
        pygame.display.set_icon(icon)
    except Exception:
        pass

    from src.core.game import Game
    game = Game(screen)

    if "--wallpaper" in args:
        game.desktop_always_on_top = True
        game.apply_desktop_settings()

    game.run()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()