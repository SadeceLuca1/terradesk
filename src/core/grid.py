"""
TerraDesk – Tile Grid
60×60 tile world with procedural terrain generation.
"""

from __future__ import annotations
import random
import math
from typing import Optional, Iterator, List
from src.core.constants import GRID_COLS, GRID_ROWS


class Tile:
    __slots__ = (
        'col', 'row', 'terrain', 'walkable', 'buildable',
        'building_id', 'road', 'elevation',
    )

    TERRAINS = ('grass', 'water', 'dirt', 'sand', 'rock', 'snow', 'path')

    def __init__(self, col: int, row: int, terrain: str = 'grass'):
        self.col = col
        self.row = row
        self.terrain = terrain
        self.walkable = terrain not in ('water',)
        self.buildable = terrain in ('grass', 'dirt', 'sand')
        self.building_id: Optional[int] = None
        self.road: bool = False
        self.elevation: float = 0.0

    def to_dict(self):
        return {
            'c': self.col, 'r': self.row, 't': self.terrain,
            'bid': self.building_id, 'rd': self.road,
        }

    @classmethod
    def from_dict(cls, d):
        t = cls(d['c'], d['r'], d.get('t', 'grass'))
        t.building_id = d.get('bid')
        t.road = d.get('rd', False)
        return t


class Grid:
    def __init__(self, cols: int = GRID_COLS, rows: int = GRID_ROWS):
        self.cols = cols
        self.rows = rows
        self._tiles: list[list[Tile]] = []
        self._generate()

    # ------------------------------------------------------------------ generation

    def _generate(self):
        rng = random.Random(42)
        # Build blank grass grid
        self._tiles = [
            [Tile(c, r, 'grass') for r in range(self.rows)]
            for c in range(self.cols)
        ]

        # Noise-like smoothed height map using simple diamond-square approximation
        h = [[0.0] * self.rows for _ in range(self.cols)]
        for _ in range(6):
            for c in range(self.cols):
                for r in range(self.rows):
                    h[c][r] += rng.uniform(-0.5, 0.5)
        # Smooth 3×3
        sh = [[0.0] * self.rows for _ in range(self.cols)]
        for c in range(self.cols):
            for r in range(self.rows):
                s, n = 0.0, 0
                for dc in range(-2, 3):
                    for dr in range(-2, 3):
                        nc, nr = c + dc, r + dr
                        if 0 <= nc < self.cols and 0 <= nr < self.rows:
                            s += h[nc][nr]
                            n += 1
                sh[c][r] = s / n if n else 0

        # Normalize
        flat = [sh[c][r] for c in range(self.cols) for r in range(self.rows)]
        mn, mx = min(flat), max(flat)
        for c in range(self.cols):
            for r in range(self.rows):
                self._tiles[c][r].elevation = (sh[c][r] - mn) / max(0.001, mx - mn)

        # Apply terrain based on elevation + border water
        for c in range(self.cols):
            for r in range(self.rows):
                tile = self._tiles[c][r]
                e = tile.elevation
                # Border water
                if c < 2 or c >= self.cols - 2 or r < 2 or r >= self.rows - 2:
                    tile.terrain = 'water'
                    tile.walkable = False
                    tile.buildable = False
                elif e < 0.25:
                    tile.terrain = 'water'
                    tile.walkable = False
                    tile.buildable = False
                elif e < 0.32:
                    tile.terrain = 'sand'
                elif e < 0.35:
                    tile.terrain = 'dirt'
                elif e > 0.85:
                    tile.terrain = 'rock'
                    tile.buildable = False
                else:
                    tile.terrain = 'grass'

        # Carve a river from NW to SE-ish
        self._carve_river(rng)

    def _carve_river(self, rng):
        c = rng.randint(10, self.cols // 3)
        r = 2
        width = rng.randint(2, 3)
        while r < self.rows - 2:
            for w in range(-width, width + 1):
                for ww in range(-width, width + 1):
                    nc, nr = c + w, r + ww
                    if 0 <= nc < self.cols and 0 <= nr < self.rows:
                        t = self._tiles[nc][nr]
                        t.terrain = 'water'
                        t.walkable = False
                        t.buildable = False
                        t.building_id = None
            # Meander
            if rng.random() < 0.3:
                c += rng.randint(-1, 1)
                c = max(4, min(self.cols - 5, c))
            r += 1

    # ------------------------------------------------------------------ access

    def get(self, col: int, row: int) -> Optional[Tile]:
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self._tiles[col][row]
        return None

    def valid(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

    def all_tiles(self) -> Iterator[Tile]:
        for col_list in self._tiles:
            yield from col_list

    # ------------------------------------------------------------------ neighbours

    def walkable_neighbours(self, col: int, row: int) -> Iterator[Tile]:
        for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            t = self.get(col + dc, row + dr)
            if t and t.walkable:
                yield t

    def walkable_neighbours_8(self, col: int, row: int) -> Iterator[Tile]:
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                t = self.get(col + dc, row + dr)
                if t and t.walkable:
                    yield t

    # ------------------------------------------------------------------ building placement

    def place_building(self, col: int, row: int, bid: int,
                       width: int = 1, height: int = 1) -> bool:
        """Mark tiles occupied. Returns False if any tile is unavailable."""
        for dc in range(width):
            for dr in range(height):
                t = self.get(col + dc, row + dr)
                if not t or not t.buildable or t.building_id is not None:
                    return False
        for dc in range(width):
            for dr in range(height):
                t = self._tiles[col + dc][row + dr]
                t.building_id = bid
                t.walkable = False
        return True

    def remove_building(self, col: int, row: int, width: int = 1, height: int = 1):
        for dc in range(width):
            for dr in range(height):
                t = self.get(col + dc, row + dr)
                if t:
                    t.building_id = None
                    if t.terrain not in ('water',):
                        t.walkable = True

    def place_road(self, col: int, row: int) -> bool:
        t = self.get(col, row)
        if not t or not t.buildable:
            return False
        t.road = True
        t.walkable = True
        return True

    # ------------------------------------------------------------------ serialise

    def to_dict(self):
        return {
            'cols': self.cols,
            'rows': self.rows,
            'tiles': [t.to_dict() for col in self._tiles for t in col],
        }

    @classmethod
    def from_dict(cls, d):
        g = cls.__new__(cls)
        g.cols = d['cols']
        g.rows = d['rows']
        g._tiles = [[None] * g.rows for _ in range(g.cols)]
        for td in d['tiles']:
            t = Tile.from_dict(td)
            g._tiles[t.col][t.row] = t
        # Fill any missing
        for c in range(g.cols):
            for r in range(g.rows):
                if g._tiles[c][r] is None:
                    g._tiles[c][r] = Tile(c, r)
        return g