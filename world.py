import random
from dataclasses import dataclass
from organism import Organism
from config import (
    WORLD_WIDTH, WORLD_HEIGHT,
    START_ORGS, START_FOOD, MAX_FOOD, FOOD_RESPAWN, TARGET_POP
)

@dataclass
class Food:
    x: float
    y: float

class World:
    def __init__(self, rng=None):
        self.rng = random.Random() if rng is None else rng
        self.orgs = []
        self.foods = []
        self.time = 0.0
        self.births = 0
        self.deaths = 0
        self.mutations = 0
        self.generation_high = 0

    def reset(self):
        self.orgs = [
            Organism(self.rng.uniform(0, WORLD_WIDTH), self.rng.uniform(0, WORLD_HEIGHT))
            for _ in range(START_ORGS)
        ]
        self.foods = [
            Food(self.rng.uniform(0, WORLD_WIDTH), self.rng.uniform(0, WORLD_HEIGHT))
            for _ in range(START_FOOD)
        ]
        self.time = 0.0
        self.births = self.deaths = self.mutations = 0
        self.generation_high = 0

    def step(self, dt):
        self.time += dt
        new_orgs = []

        for o in list(self.orgs):
            if not o.alive:
                continue
            ate = o.step(dt, self.foods, self.rng)

            # Probabilistic, population-aware respawn
            if ate and FOOD_RESPAWN and len(self.foods) < MAX_FOOD:
                k = max(0.15, 1.0 - (len(self.orgs) / max(1, TARGET_POP)))
                if random.random() < k:
                    self.foods.append(Food(self.rng.uniform(0, WORLD_WIDTH),
                                           self.rng.uniform(0, WORLD_HEIGHT)))

            if o.can_reproduce():
                child = o.reproduce(self.rng)
                new_orgs.append(child)
                self.births += 1
                self.mutations += 1
                if child.gen > self.generation_high:
                    self.generation_high = child.gen

            if not o.alive:
                self.deaths += 1

        self.orgs = [o for o in self.orgs if o.alive]
        self.orgs.extend(new_orgs)

        if len(self.foods) > MAX_FOOD:
            self.foods = self.foods[:MAX_FOOD]

    def population(self):
        return len(self.orgs)

    def master_default(self):
        return self.orgs[0] if self.orgs else None

    def avg_traits(self):
        if not self.orgs: return (0,0,0,0)
        n = len(self.orgs)
        fov = sum(o.trait_fov_deg for o in self.orgs)/n
        rng = sum(o.trait_range for o in self.orgs)/n
        thr = sum(o.trait_thrust_eff for o in self.orgs)/n
        met = sum(o.trait_metabolism_eff for o in self.orgs)/n
        return fov, rng, thr, met
