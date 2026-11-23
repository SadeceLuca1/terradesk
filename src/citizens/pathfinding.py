"""
TerraDesk – A* Pathfinding
Finds walkable paths on the isometric grid.
"""

from __future__ import annotations
import heapq
import math
from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.grid import Grid

Point = Tuple[int, int]


def heuristic(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def find_path(grid: "Grid", start: Point, goal: Point,
              max_steps: int = 500) -> Optional[List[Point]]:
    """
    A* pathfinding. Returns list of (col,row) points from start to goal,
    or None if no path found.
    """
    if start == goal:
        return [start]

    st = grid.get(*start)
    gt = grid.get(*goal)
    if st is None or gt is None:
        return None
    # Allow goal even if not normally walkable (building entrance)

    open_heap = []
    heapq.heappush(open_heap, (0.0, start))
    came_from: dict[Point, Optional[Point]] = {start: None}
    g_score: dict[Point, float] = {start: 0.0}
    steps = 0

    while open_heap and steps < max_steps:
        steps += 1
        _, current = heapq.heappop(open_heap)

        if current == goal:
            return _reconstruct(came_from, current)

        for tile in grid.walkable_neighbours_8(*current):
            nb = (tile.col, tile.row)
            # Diagonal cost
            is_diag = (nb[0] != current[0] and nb[1] != current[1])
            move_cost = 1.414 if is_diag else 1.0
            tentative_g = g_score[current] + move_cost

            if nb not in g_score or tentative_g < g_score[nb]:
                g_score[nb] = tentative_g
                f = tentative_g + heuristic(nb, goal)
                heapq.heappush(open_heap, (f, nb))
                came_from[nb] = current

    # Path not found – return partial path toward goal
    if came_from:
        best = min(came_from.keys(), key=lambda p: heuristic(p, goal))
        if best != start:
            return _reconstruct(came_from, best)
    return None


def _reconstruct(came_from: dict, current: Point) -> List[Point]:
    path = []
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path