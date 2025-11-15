import math
from typing import Optional

import pygame

from config import FOV_COLOR, TARGET_COLOR


def draw_fov(surface: pygame.Surface, agent) -> None:
    """
    Draw the agent's field of view as two rays plus a faint arc.

    Assumes the agent exposes:
        - x, y              (position)
        - angle             (heading, radians)
        - trait_fov_deg     (FOV in degrees)
        - trait_range       (max sensor range)
    """
    fov_rad = math.radians(agent.trait_fov_deg) / 2.0
    x, y = float(agent.x), float(agent.y)

    left_ang = agent.angle - fov_rad
    right_ang = agent.angle + fov_rad

    left = (
        x + agent.trait_range * math.cos(left_ang),
        y + agent.trait_range * math.sin(left_ang),
    )
    right = (
        x + agent.trait_range * math.cos(right_ang),
        y + agent.trait_range * math.sin(right_ang),
    )

    # boundary rays
    pygame.draw.line(surface, FOV_COLOR, (x, y), left, 1)
    pygame.draw.line(surface, FOV_COLOR, (x, y), right, 1)

    # arc between left and right
    steps = 24
    pts = []
    for i in range(steps + 1):
        a = left_ang + (i / steps) * (right_ang - left_ang)
        px = x + agent.trait_range * math.cos(a)
        py = y + agent.trait_range * math.sin(a)
        pts.append((px, py))

    if len(pts) >= 2:
        pygame.draw.aalines(surface, FOV_COLOR, False, pts, 1)


def draw_target(surface: pygame.Surface, agent) -> None:
    """
    Draw a line from the agent to its last seen target, if any.

    Assumes:
        - agent.last_seen_target is either None or an object with .x, .y
    """
    target: Optional[object] = getattr(agent, "last_seen_target", None)
    if target is None:
        return

    fx, fy = float(target.x), float(target.y)
    pygame.draw.aaline(surface, TARGET_COLOR, (agent.x, agent.y), (fx, fy), 1)
