import math
import time
import random
import pygame
import sys

from world import World, Food
from logger import Logger
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    FPS,
    BG_COLOR,
    GRID_COLOR,
    DRAW_GRID,
    GRID_SPACING,
    DRAW_FOV,
    ORG_COLOR,
    ORG_GLOW,
    FOOD_COLOR,
    FOOD_GLOW,
    HOME_RADIUS,
    HOME_BUILD_ENERGY_COST,
)

from utils import clamp


def draw_grid(surface):
    """Subtle grid background for visualization."""
    for x in range(0, WORLD_WIDTH, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WORLD_HEIGHT), 1)
    for y in range(0, WORLD_HEIGHT, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WORLD_WIDTH, y), 1)


def draw_food(surface, food_list):
    """Draw food particles with a soft glow."""
    for f in food_list:
        # Glow
        pygame.draw.circle(surface, FOOD_GLOW, (int(f.x), int(f.y)), 5)
        # Core
        pygame.draw.circle(surface, FOOD_COLOR, (int(f.x), int(f.y)), 3)


def draw_home(surface, pos):
    """Draw simple home circle."""
    if pos is None:
        return
    x, y = pos
    pygame.draw.circle(surface, (100, 200, 255), (int(x), int(y)), int(HOME_RADIUS), 1)


def draw_organism(surface, org, draw_fov=False):
    """Draw organisms with orientation, FOV arcs, home markers, and trails."""

    x = int(org.x)
    y = int(org.y)
    angle = org.angle

    # Glow behind organism
    pygame.draw.circle(surface, ORG_GLOW, (x, y), 9)

    # Body
    pygame.draw.circle(surface, ORG_COLOR, (x, y), 5)

    # Heading
    hx = x + int(math.cos(angle) * 10)
    hy = y + int(math.sin(angle) * 10)
    pygame.draw.line(surface, (255, 255, 255), (x, y), (hx, hy), 2)

    # Home
    if org.home_pos:
        draw_home(surface, org.home_pos)

    # Trail (optional)
    if len(org.trail) > 1:
        pts = [(int(px), int(py)) for (px, py) in org.trail]
        pygame.draw.lines(surface, (100, 255, 140), False, pts, 1)

    # FOV overlay
    if draw_fov:
        fov_rad = math.radians(org.trait_fov_deg)
        left = angle - fov_rad / 2
        right = angle + fov_rad / 2

        lx = x + int(math.cos(left) * org.trait_range)
        ly = y + int(math.sin(left) * org.trait_range)
        rx = x + int(math.cos(right) * org.trait_range)
        ry = y + int(math.sin(right) * org.trait_range)

        pygame.draw.line(surface, (0, 200, 100), (x, y), (lx, ly), 1)
        pygame.draw.line(surface, (0, 200, 100), (x, y), (rx, ry), 1)


def draw_weather_overlay(surface, env):
    """
    Draw small weather UI: temperature, precipitation, day/night bar.
    """
    font = pygame.font.SysFont("consolas", 16)
    temp_text = f"{env.last_global_growth_rate:.3f} growth"
    precip = f"precip={env.precipitation:.2f}"
    day = f"day={env.day_night_factor:.2f}"

    txt = f"{temp_text}   {precip}   {day}"

    surf = font.render(txt, True, (255, 255, 255))
    surface.blit(surf, (10, 10))


def main():
    pygame.init()
    pygame.display.set_caption("Micro-Organism World Simulation")
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
    clock = pygame.time.Clock()

    rng = random.Random(12345)

    # World + logger
    world = World(rng)
    world.reset()
    logger = Logger()

    running = True
    sim_speed = 1.0  # multiplier for dt (can speed up/slow down simulation)

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt *= sim_speed

        # Handle events / keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    print("Resetting world...")
                    world.reset()

                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    sim_speed = clamp(sim_speed + 0.1, 0.1, 10.0)
                    print(f"Speed = {sim_speed:.1f}x")

                elif event.key == pygame.K_MINUS:
                    sim_speed = clamp(sim_speed - 0.1, 0.1, 10.0)
                    print(f"Speed = {sim_speed:.1f}x")

        # Update world
        world.step(dt)

        # Logging
        logger.maybe_print(world)
        logger.log_csv(world)

        # Draw background
        screen.fill(BG_COLOR)
        if DRAW_GRID:
            draw_grid(screen)

        # Draw food
        draw_food(screen, world.foods)

        # Draw organisms
        for o in world.orgs:
            draw_organism(screen, o, DRAW_FOV)

        # Weather overlay
        draw_weather_overlay(screen, world.env)

        # Update screen
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
