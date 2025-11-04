import math, pygame
from config import FOV_COLOR, TARGET_COLOR

def draw_fov(surface, agent):
    # draw two rays for FOV and a faint arc
    fov_rad = math.radians(agent.trait_fov_deg) / 2.0
    x, y = agent.x, agent.y
    left_ang = agent.angle - fov_rad
    right_ang = agent.angle + fov_rad

    left = (x + agent.trait_range*math.cos(left_ang),
            y + agent.trait_range*math.sin(left_ang))
    right = (x + agent.trait_range*math.cos(right_ang),
             y + agent.trait_range*math.sin(right_ang))
    pygame.draw.line(surface, FOV_COLOR, (x, y), left, 1)
    pygame.draw.line(surface, FOV_COLOR, (x, y), right, 1)

    # arc
    steps = 20
    pts = []
    for i in range(steps+1):
        a = left_ang + (i/steps)*(right_ang-left_ang)
        pts.append((x + agent.trait_range*math.cos(a), y + agent.trait_range*math.sin(a)))
    pygame.draw.aalines(surface, FOV_COLOR, False, pts, 1)

def draw_target(surface, agent):
    if agent.last_seen_target is None: return
    fx, fy = agent.last_seen_target.x, agent.last_seen_target.y
    pygame.draw.aaline(surface, TARGET_COLOR, (agent.x, agent.y), (fx, fy), 1)
