import math
from config import WORLD_WIDTH, WORLD_HEIGHT

def torus_delta(ax, ay, bx, by):
    dx = bx - ax; dy = by - ay
    if dx >  WORLD_WIDTH/2:  dx -= WORLD_WIDTH
    if dx < -WORLD_WIDTH/2:  dx += WORLD_WIDTH
    if dy >  WORLD_HEIGHT/2: dy -= WORLD_HEIGHT
    if dy < -WORLD_HEIGHT/2: dy += WORLD_HEIGHT
    return dx, dy

def angle_diff(a, b):
    d = (a - b + math.pi) % (2*math.pi) - math.pi
    return d

def raycast_cone(agent, foods, fov_rad, rng_len, rays):
    """Return (left_signal, right_signal, nearest_food_obj or None) using multi-ray sampling."""
    if rays < 3: rays = 3
    half = fov_rad / 2.0
    step = (2*half) / (rays - 1)
    left = right = 0.0
    nearest = None; nearest_dist = 1e9

    for i in range(rays):
        rel = -half + i*step  # left -> right
        ray_angle = (agent.angle + rel)
        for f in foods:
            dx, dy = torus_delta(agent.x, agent.y, f.x, f.y)
            dist = math.hypot(dx, dy)
            if dist > rng_len:
                continue
            ang_to = math.atan2(dy, dx)
            ang_err = abs(angle_diff(ang_to, ray_angle))
            if ang_err > (step * 0.75):
                continue
            contrib = max(0.0, 1.0 - dist / rng_len)
            if rel < 0:
                left = max(left, contrib)
            else:
                right = max(right, contrib)
            if dist < nearest_dist:
                nearest_dist, nearest = dist, f

    return left, right, nearest
