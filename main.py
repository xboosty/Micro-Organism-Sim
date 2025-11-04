import math, sys, pygame, random
from config import (
    WORLD_WIDTH, WORLD_HEIGHT, FPS, BG_COLOR, BG_VIGNETTE_ALPHA,
    FOOD_COLOR, FOOD_GLOW, FOOD_RADIUS,
    ORG_COLOR, ORG_GLOW, MASTER_COLOR,
    FOV_COLOR, TARGET_COLOR,
    DRAW_FOV, STATUS_PRINT_INTERVAL,
    DRAW_GRID, GRID_SPACING,
    MASTER_TRAIL_ALPHA
)
from world import World
from stats import Stats
from master_view import draw_fov, draw_target

def make_vignette(size):
    """Create a radial dark vignette surface."""
    w, h = size
    surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
    cx, cy = w/2, h/2
    maxd = (cx**2 + cy**2) ** 0.5
    for y in range(h):
        for x in range(w):
            dx = x - cx; dy = y - cy
            d = (dx*dx + dy*dy) ** 0.5
            a = int((d / maxd) * BG_VIGNETTE_ALPHA)
            if a <= 0: continue
            surf.set_at((x, y), (0, 0, 0, min(255, a)))
    return surf

def make_glow_surface(radius, color, alpha=120):
    """Soft glow disk used for food / organisms."""
    size = radius*4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for r in range(radius*2, 0, -1):
        a = int(alpha * (r / (radius*2)))
        pygame.draw.circle(surf, (*color, a), (cx, cy), r)
    return surf

def draw_grid(screen):
    if not DRAW_GRID: return
    w, h = screen.get_size()
    for x in range(0, w, GRID_SPACING):
        pygame.draw.line(screen, (18,24,34), (x, 0), (x, h), 1)
    for y in range(0, h, GRID_SPACING):
        pygame.draw.line(screen, (18,24,34), (0, y), (w, y), 1)

def draw_world(screen, world, master=None, debug=False, glows=None, vignette=None, font=None):
    # background base
    screen.fill(BG_COLOR)
    draw_grid(screen)

    # foods (with soft glow)
    glow_food = glows["food"]
    for f in world.foods:
        gx = int(f.x - glow_food.get_width()/2)
        gy = int(f.y - glow_food.get_height()/2)
        screen.blit(glow_food, (gx, gy))
        pygame.draw.circle(screen, FOOD_COLOR, (int(f.x), int(f.y)), FOOD_RADIUS)

    # organisms
    glow_org = glows["org"]
    for o in world.orgs:
        is_master = (master and o.id == master.id)
        color = MASTER_COLOR if is_master else ORG_COLOR

        gx = int(o.x - glow_org.get_width()/2)
        gy = int(o.y - glow_org.get_height()/2)
        if is_master:
            # brighter glow for master (double blit)
            screen.blit(glow_org, (gx, gy))
        screen.blit(glow_org, (gx, gy))

        pygame.draw.circle(screen, color, (int(o.x), int(o.y)), 5)
        # heading tick
        hx = o.x + 10*math.cos(o.angle)
        hy = o.y + 10*math.sin(o.angle)
        pygame.draw.line(screen, color, (o.x, o.y), (hx, hy), 2)

    # debug for master (FOV, target, and trail)
    if debug and master:
        draw_fov(screen, master)
        draw_target(screen, master)
        if len(master.trail) > 2:
            # draw faded trail
            pts = list(master.trail)
            for i in range(1, len(pts)):
                p1 = pts[i-1]; p2 = pts[i]
                alpha = int(MASTER_TRAIL_ALPHA * (i / len(pts)))
                col = (*MASTER_COLOR, alpha)
                s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.aaline(s, col, p1, p2, 1)
                screen.blit(s, (0,0))

    # vignette overlay
    if vignette:
        screen.blit(vignette, (0,0))

def draw_hud(screen, world, master, sim_speed, paused, font):
    hud1 = f"Pop:{world.population():3d}  Food:{len(world.foods):3d}  Time:{world.time:7.1f}s  x{sim_speed:.2f}"
    hud2 = "[SPACE] pause  [-][=] speed  [1..5] presets  [D] debug  [R] reset  [F] more food  (click to set master)"
    color = (220, 230, 245)
    small = (180, 190, 210)

    surf1 = font.render(hud1 + ("   [PAUSED]" if paused else ""), True, color)
    surf2 = font.render(hud2, True, small)
    screen.blit(surf1, (12, 10))
    screen.blit(surf2, (12, 36))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
    pygame.display.set_caption("Evolution Sim (Time Control, Traits, Physics)")
    clock = pygame.time.Clock()

    # assets
    vignette = make_vignette((WORLD_WIDTH, WORLD_HEIGHT))
    glow_food = make_glow_surface(6, FOOD_GLOW, alpha=140)
    glow_org  = make_glow_surface(7, ORG_GLOW,  alpha=90)
    glows = {"food": glow_food, "org": glow_org}
    font = pygame.font.SysFont("menlo,consolas,dejavusansmono", 18)

    rng = random.Random()
    world = World(rng)
    world.reset()

    master = world.master_default()
    debug = True
    stats = Stats(world, interval=STATUS_PRINT_INTERVAL)

    running = True
    paused = False
    sim_speed = 1.0   # time dilation multiplier

    while running:
        dt = clock.tick(FPS) / 1000.0

        # EVENTS / HOTKEYS
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_SPACE: paused = not paused
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_RIGHTBRACKET):
                    sim_speed = min(8.0, sim_speed + 0.25)
                elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE, pygame.K_LEFTBRACKET):
                    sim_speed = max(0.1, sim_speed - 0.25)
                elif event.key == pygame.K_1: sim_speed = 0.25
                elif event.key == pygame.K_2: sim_speed = 0.5
                elif event.key == pygame.K_3: sim_speed = 1.0
                elif event.key == pygame.K_4: sim_speed = 2.0
                elif event.key == pygame.K_5: sim_speed = 4.0
                elif event.key == pygame.K_d: debug = not debug
                elif event.key == pygame.K_r:
                    world.reset(); master = world.master_default()
                elif event.key == pygame.K_f:
                    from world import Food
                    for _ in range(25):
                        world.foods.append(Food(rng.uniform(0, WORLD_WIDTH), rng.uniform(0, WORLD_HEIGHT)))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                mind, pick = 1e9, None
                for o in world.orgs:
                    d2 = (o.x - mx)**2 + (o.y - my)**2
                    if d2 < mind:
                        mind, pick = d2, o
                master = pick

        # SIM STEP
        if not paused:
            world.step(dt * sim_speed)

        # Fallback master
        if master is None or not master.alive:
            master = world.master_default()

        # DRAW
        draw_world(screen, world, master=master, debug=debug and DRAW_FOV,
                   glows=glows, vignette=vignette, font=font)
        draw_hud(screen, world, master, sim_speed, paused, font)
        pygame.display.flip()

        # STATS
        if master:
            stats.maybe_print(master)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
