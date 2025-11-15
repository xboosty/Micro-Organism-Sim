import math
from typing import List, Tuple

from config import WORLD_WIDTH, WORLD_HEIGHT


def torus_delta(ax: float, ay: float, bx: float, by: float) -> Tuple[float, float]:
    """
    Smallest vector from (ax, ay) to (bx, by) on a torus world.
    """
    dx = bx - ax
    dy = by - ay

    half_w = WORLD_WIDTH / 2.0
    half_h = WORLD_HEIGHT / 2.0

    if dx > half_w:
        dx -= WORLD_WIDTH
    elif dx < -half_w:
        dx += WORLD_WIDTH

    if dy > half_h:
        dy -= WORLD_HEIGHT
    elif dy < -half_h:
        dy += WORLD_HEIGHT

    return dx, dy


def angle_diff(a: float, b: float) -> float:
    """
    Smallest signed difference between two angles a and b (radians) in [-pi, pi].
    """
    d = (a - b + math.pi) % (2.0 * math.pi) - math.pi
    return d


def raycast_cone(
    x: float,
    y: float,
    angle: float,
    fov_rad: float,
    rng_len: float,
    rays: int,
    foods,
) -> List[Tuple[float, float]]:
    """
    Very lightweight cone "raycast" over food particles.

    For now we don't march true rays through tiles; instead we:

    - Treat the cone as a continuous FOV centered on `angle` with width fov_rad.
    - For each food item:
        * Compute wrapped dx, dy using torus geometry.
        * Compute distance and bearing relative to the organism.
        * If within range AND within FOV, we record it as a "hit".

    Returns:
        List of (relative_angle, distance) tuples for all hits,
        where relative_angle = angle_to_food - angle, in radians.
        Negative values = to the left, positive = to the right.

    The `rays` parameter is currently unused but kept for API compatibility
    and future extension to true ray-marching against terrain.
    """
    hits: List[Tuple[float, float]] = []
    half_fov = fov_rad / 2.0

    if not foods:
        return hits

    for f in foods:
        dx, dy = torus_delta(x, y, f.x, f.y)
        dist = math.hypot(dx, dy)
        if dist <= 0.0 or dist > rng_len:
            continue

        ang_to = math.atan2(dy, dx)
        rel = angle_diff(ang_to, angle)

        if abs(rel) <= half_fov:
            hits.append((rel, dist))

    return hits
