# utils.py
"""
Utility helpers for math, interpolation, and wrapping.

These are intentionally lightweight so they can be shared across
rendering, physics, and stats without pulling in heavy dependencies.
"""

import math
from typing import Tuple


def clamp(x: float, a: float, b: float) -> float:
    """Clamp x to the closed interval [a, b]."""
    return a if x < a else b if x > b else x


def wrap_pos(x: float, y: float, w: float, h: float) -> Tuple[float, float]:
    """
    Wrap a 2D position into [0,w) × [0,h), useful for torus-style worlds.
    """
    if x < 0:
        x += w
    if x >= w:
        x -= w
    if y < 0:
        y += h
    if y >= h:
        y -= h
    return x, y


def angle_wrap(a: float) -> float:
    """
    Wrap an angle (radians) into the interval (-pi, pi].
    """
    while a <= -math.pi:
        a += 2 * math.pi
    while a > math.pi:
        a -= 2 * math.pi
    return a


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between a and b by t in [0,1].
    """
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """
    Smooth Hermite interpolation between 0 and 1 when x is in [edge0, edge1].

    Useful for soft transitions (e.g., visual fades, soft thresholds).
    """
    if edge0 == edge1:
        return 0.0
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def remap(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    Remap x from [in_min, in_max] into [out_min, out_max] linearly.
    """
    if in_max == in_min:
        return out_min
    t = (x - in_min) / (in_max - in_min)
    return out_min + (out_max - out_min) * t
