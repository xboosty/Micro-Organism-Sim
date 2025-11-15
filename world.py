import math
import random
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Set

from organism import Organism
from vision import torus_delta
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    START_ORGS,
    START_FOOD,
    MAX_FOOD,
    FOOD_RESPAWN,
    TARGET_POP,
    START_ADAM_EVE,
    # environment / weather
    DAY_LENGTH,
    YEAR_LENGTH,
    BASE_TEMPERATURE_EQUATOR,
    BASE_TEMPERATURE_POLE,
    SEASONAL_VARIATION_EQUATOR,
    SEASONAL_VARIATION_POLE,
    BASE_PRECIPITATION,
    PRECIP_VARIATION,
    PRECIP_NOISE,
    BASE_REGROWTH,
    GROWTH_NOISE,
    OPTIMAL_GROWTH_TEMP,
    TEMP_TOLERANCE,
    # reproduction
    SEXUAL_REPRODUCTION,
    MATING_RADIUS,
    MATING_DRIVE_STRENGTH,
)

# --------------------------------------------------------------------- #
# Simple Food object
# --------------------------------------------------------------------- #


@dataclass
class Food:
    x: float
    y: float


# --------------------------------------------------------------------- #
# Environment: weather, seasons, growth factors
# --------------------------------------------------------------------- #


class Environment:
    """
    Earth-ish environment with:

    - Day/night cycle
    - Seasonal cycle
    - Latitude-dependent temperature
    - Global precipitation
    - Weather-dependent growth factor for food regrowth

    Currently global & uniform, but growth_rate_at(y) is written to
    easily extend to spatial variation (per-tile or per-region) later.
    """

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.rng: random.Random = random.Random() if rng is None else rng
        self.time: float = 0.0

        self.day_night_factor: float = 1.0  # 0 = deep night, 1 = noon
        self.season_phase: float = 0.0      # 0..1 over a “year”
        self.precipitation: float = BASE_PRECIPITATION  # 0..1
        self.last_global_growth_rate: float = BASE_REGROWTH

    # ----------------------------- #
    # Core update
    # ----------------------------- #

    def update(self, dt: float) -> None:
        self.time += dt

        # Day/night phase [0,1)
        day_phase = (self.time % DAY_LENGTH) / max(DAY_LENGTH, 1e-6)
        # Use a cosine to get smooth day/night: 0 at midnight, 1 at noon
        self.day_night_factor = 0.5 * (1.0 - math.cos(2.0 * math.pi * day_phase))

        # Seasonal phase [0,1)
        self.season_phase = (self.time % YEAR_LENGTH) / max(YEAR_LENGTH, 1e-6)

        # Precipitation: base + seasonal oscillation + noise, clamped to [0,1]
        base_precip = BASE_PRECIPITATION + PRECIP_VARIATION * math.cos(
            2.0 * math.pi * self.season_phase
        )
        noise = self.rng.uniform(-PRECIP_NOISE, PRECIP_NOISE)
        self.precipitation = max(0.0, min(1.0, base_precip + noise))

        # Track a default global growth rate at mid-latitude (for debugging/insight)
        mid_y = WORLD_HEIGHT / 2.0
        self.last_global_growth_rate = self.growth_rate_at(mid_y)

    # ----------------------------- #
    # Temperature & growth helpers
    # ----------------------------- #

    @staticmethod
    def _lat_from_y(y: float) -> float:
        """
        Map y in [0, WORLD_HEIGHT] to |latitude| in [0,1].
        0 = equator, 1 = pole.
        Middle of the map = equator; top/bottom = poles.
        """
        ny = y / max(WORLD_HEIGHT, 1e-6)
        # Map [0,1] -> [-1,1], then take abs: equator at 0.5
        lat = abs(2.0 * ny - 1.0)
        return max(0.0, min(1.0, lat))

    def temperature_at_y(self, y: float) -> float:
        """
        Latitude + season dependent temperature (°C).
        """
        lat = self._lat_from_y(y)
        base_temp = BASE_TEMPERATURE_POLE + (BASE_TEMPERATURE_EQUATOR - BASE_TEMPERATURE_POLE) * (
            1.0 - lat
        )
        seasonal_amp = SEASONAL_VARIATION_POLE + (
            SEASONAL_VARIATION_EQUATOR - SEASONAL_VARIATION_POLE
        ) * (1.0 - lat)

        season_term = seasonal_amp * math.cos(2.0 * math.pi * self.season_phase)
        temp = base_temp + season_term
        return temp

    def growth_rate_at(self, y: float) -> float:
        """
        Weather-dependent growth rate (per-second probability scale) at a given y.

        growth ≈ BASE_REGROWTH * temp_factor * precip_factor * day_factor + noise
        """
        temp = self.temperature_at_y(y)

        # Temperature factor: peaked around OPTIMAL_GROWTH_TEMP, falls off with squared distance
        diff = abs(temp - OPTIMAL_GROWTH_TEMP)
        temp_factor = max(0.0, 1.0 - (diff / max(TEMP_TOLERANCE, 1e-6)) ** 2)

        # Precipitation factor: ensure non-zero even when dry
        precip_factor = 0.3 + 0.7 * self.precipitation

        # Day/night: more growth during “day”
        day_factor = 0.3 + 0.7 * self.day_night_factor

        growth = BASE_REGROWTH * temp_factor * precip_factor * day_factor
        noise = self.rng.uniform(-GROWTH_NOISE, GROWTH_NOISE)
        growth = max(0.0, growth + noise)
        return growth

    def global_growth_rate(self) -> float:
        """
        Convenience: growth rate at map midpoint.
        """
        return self.last_global_growth_rate


# --------------------------------------------------------------------- #
# World: organisms + food + environment
# --------------------------------------------------------------------- #


class World:
    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.rng: random.Random = random.Random() if rng is None else rng
        self.env: Environment = Environment(self.rng)

        self.orgs: List[Organism] = []
        self.foods: List[Food] = []

        self.time: float = 0.0
        self.births: int = 0
        self.deaths: int = 0
        self.mutations: int = 0
        self.generation_high: int = 0

    # ----------------------------- #
    # Reset / initialization
    # ----------------------------- #

    def reset(self) -> None:
        """
        Reset the entire world.

        If START_ADAM_EVE is True, we start with two organisms at the center
        (one male, one female) and let the world evolve from them.
        Otherwise, we spawn START_ORGS random organisms.
        """
        self.time = 0.0
        self.births = self.deaths = self.mutations = 0
        self.generation_high = 0

        # Reset environment
        self.env = Environment(self.rng)

        if START_ADAM_EVE:
            cx = WORLD_WIDTH / 2.0
            cy = WORLD_HEIGHT / 2.0
            adam = Organism(cx - 20.0, cy, sex="M")
            eve = Organism(cx + 20.0, cy, sex="F")
            self.orgs = [adam, eve]
        else:
            self.orgs = [
                Organism(
                    self.rng.uniform(0, WORLD_WIDTH),
                    self.rng.uniform(0, WORLD_HEIGHT),
                )
                for _ in range(START_ORGS)
            ]

        self.foods = [
            Food(
                self.rng.uniform(0, WORLD_WIDTH),
                self.rng.uniform(0, WORLD_HEIGHT),
            )
            for _ in range(START_FOOD)
        ]

    # ----------------------------- #
    # Step
    # ----------------------------- #

    def step(self, dt: float) -> None:
        """
        Advance the entire world by dt seconds.

        Handles:
        - Environment/weather update
        - Organism stepping (movement, sensing, eating, sleep/dreams, learning)
        - Weather-dependent food regrowth
        - Asexual or sexual reproduction
        - Basic parental nurture hooks
        """
        # Update time & environment
        self.time += dt
        self.env.update(dt)

        new_orgs: List[Organism] = []
        used_for_mating: Set[int] = set()

        # Step organisms
        for o in list(self.orgs):
            if not o.alive:
                continue

            ate = o.step(dt, self.foods, self.rng, env=self.env)

            # Weather- & population-aware respawn when food is eaten
            if ate and FOOD_RESPAWN and len(self.foods) < MAX_FOOD:
                # population factor: respawn less when we are over target pop
                k_pop = max(0.15, 1.0 - (len(self.orgs) / max(1, TARGET_POP)))

                # pick a random spot and compute growth there
                fx = self.rng.uniform(0, WORLD_WIDTH)
                fy = self.rng.uniform(0, WORLD_HEIGHT)
                growth_rate = self.env.growth_rate_at(fy)  # per-second-like scale

                # approximate per-step probability
                prob = k_pop * growth_rate * dt
                prob = max(0.0, min(1.0, prob))

                if prob > 0.0 and self.rng.random() < prob:
                    self.foods.append(Food(fx, fy))

            # Count deaths
            if not o.alive:
                self.deaths += 1

        # Reproduction phase (after movement/eating)
        if SEXUAL_REPRODUCTION:
            # Sexual reproduction: find compatible mates within MATING_RADIUS
            org_list = [o for o in self.orgs if o.alive and o.can_reproduce()]
            for i, a in enumerate(org_list):
                if a.id in used_for_mating:
                    continue
                if self.rng.random() > MATING_DRIVE_STRENGTH:
                    continue

                best_partner = None
                best_d2 = MATING_RADIUS * MATING_RADIUS

                for j in range(i + 1, len(org_list)):
                    b = org_list[j]
                    if b.id in used_for_mating:
                        continue
                    if a.sex == b.sex:
                        continue
                    # distance on torus
                    dx, dy = torus_delta(a.x, a.y, b.x, b.y)
                    d2 = dx * dx + dy * dy
                    if d2 <= best_d2:
                        best_d2 = d2
                        best_partner = b

                if best_partner is not None:
                    child = Organism.reproduce_sexual(a, best_partner, self.rng)
                    if child is not None:
                        new_orgs.append(child)
                        self.births += 1
                        self.mutations += 1
                        if child.gen > self.generation_high:
                            self.generation_high = child.gen
                        used_for_mating.add(a.id)
                        used_for_mating.add(best_partner.id)
        else:
            # Asexual reproduction
            for o in list(self.orgs):
                if not o.alive:
                    continue
                if o.can_reproduce():
                    child = o.reproduce_asexual(self.rng)
                    new_orgs.append(child)
                    self.births += 1
                    self.mutations += 1
                    if child.gen > self.generation_high:
                        self.generation_high = child.gen

        # Remove dead organisms, add newborns
        self.orgs = [o for o in self.orgs if o.alive]
        self.orgs.extend(new_orgs)

        # Parental nurture phase: parents can build homes & feed dependents
        id_map: Dict[int, Organism] = {o.id: o for o in self.orgs}
        cared_children: Set[int] = set()

        for parent in self.orgs:
            if not parent.dependents:
                continue

            # Encourage home building for parents
            parent.maybe_build_home()

            for child_id in list(parent.dependents):
                child = id_map.get(child_id)
                if child is None or not child.alive:
                    continue
                parent.nurture_child(child)
                cared_children.add(child.id)

        # Optional: apply a mild orphan penalty to children without caregivers
        # (you can tune or expand this later)
        for child in self.orgs:
            # quick check: only for “young” organisms
            from config import CHILD_DEPENDENCY_AGE, ORPHAN_PENALTY  # local import to avoid cycle

            if child.age < CHILD_DEPENDENCY_AGE and child.id not in cared_children:
                # Small extra energy drain if no caregivers
                child.energy -= (1.0 - ORPHAN_PENALTY) * 0.01 * dt
                if child.energy <= 0.0:
                    child.alive = False
                    self.deaths += 1

        # Trim food list if over capacity (hard cap)
        if len(self.foods) > MAX_FOOD:
            self.foods = self.foods[:MAX_FOOD]

    # ----------------------------- #
    # Convenience / stats
    # ----------------------------- #

    def population(self) -> int:
        return len(self.orgs)

    def master_default(self) -> Optional[Organism]:
        return self.orgs[0] if self.orgs else None

    def avg_traits(self) -> Tuple[float, float, float, float]:
        if not self.orgs:
            return 0.0, 0.0, 0.0, 0.0
        n = len(self.orgs)
        fov = sum(o.trait_fov_deg for o in self.orgs) / n
        rng = sum(o.trait_range for o in self.orgs) / n
        thr = sum(o.trait_thrust_eff for o in self.orgs) / n
        met = sum(o.trait_metabolism_eff for o in self.orgs) / n
        return fov, rng, thr, met
