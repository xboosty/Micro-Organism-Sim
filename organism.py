import math
import random
from collections import deque
from typing import Optional, Tuple, Set

import numpy as np
import torch

from brain import Brain
from vision import torus_delta, raycast_cone
from genetics import inherit_traits, mutate_val
from config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    BASE_THRUST,
    MAX_TURN_TORQUE,
    LIN_DRAG,
    ANG_DRAG,
    MAX_SPEED,
    SENSOR_RANGE_DEFAULT,
    SENSOR_FOV_DEG_DEFAULT,
    SENSOR_RAYS,
    START_ENERGY,
    METABOLISM_BASE,
    METABOLISM_SPEED_COEF,
    METABOLISM_BRAIN_COEF,
    FOOD_ENERGY,
    EAT_RADIUS,
    REPRODUCTION_THRESHOLD,
    PARENT_KEEP,
    CHILD_TAKE,
    SEXUAL_REPRODUCTION,
    MATING_RADIUS,
    MATING_DRIVE_STRENGTH,
    MAX_AGE,
    MASTER_TRAIL_POINTS,
    # brain/dev
    DEV_LEARNING_AGE_HALF,
    DEV_LEARNING_MIN,
    # sleep / dreams
    SLEEP_PRESSURE_RATE,
    SLEEP_RECOVERY_RATE,
    SLEEP_MIN_PRESSURE,
    SLEEP_NIGHT_WEIGHT,
    SLEEP_METABOLISM_FACTOR,
    DREAM_STEPS_PER_SEC,
    MEMORY_BUFFER_SIZE,
    # homes / nurture
    CAN_BUILD_HOMES,
    HOME_BUILD_ENERGY_COST,
    HOME_RADIUS,
    CHILD_DEPENDENCY_AGE,
    PARENT_FEED_SHARE,
    ORPHAN_PENALTY,
    # trait bounds for sexual inheritance
    FOV_MIN,
    FOV_MAX,
    RANGE_MIN,
    RANGE_MAX,
    THRUST_MIN,
    THRUST_MAX,
    META_MIN,
    META_MAX,
)


class Organism:
    """
    A self-propelled micro-organism with:
    - Recurrent neural controller (Brain) with plasticity (on GPU if available).
    - Heritable traits (vision FOV, sensor range, thrust and metabolism efficiency).
    - Sex (M/F) and support for both asexual and sexual reproduction.
    - Sleep / dream cycles with offline learning.
    - Hooks for homes / parental care (nature + nurture).
    """

    _next_id = 0

    def __init__(
        self,
        x: float,
        y: float,
        angle: Optional[float] = None,
        energy: float = START_ENERGY,
        brain: Optional[Brain] = None,
        gen: int = 0,
        fov_deg: float = SENSOR_FOV_DEG_DEFAULT,
        rng_len: float = SENSOR_RANGE_DEFAULT,
        thrust_eff: float = 1.0,
        metabolism_eff: float = 1.0,
        sex: Optional[str] = None,
        parents: Optional[Tuple[int, ...]] = None,
    ) -> None:
        # identity
        self.id: int = Organism._next_id
        Organism._next_id += 1

        self.gen: int = gen
        self.parents: Tuple[int, ...] = parents if parents is not None else tuple()
        self.dependents: Set[int] = set()  # ids of children depending on this organism

        # position / motion
        self.x: float = x
        self.y: float = y
        self.angle: float = angle if angle is not None else random.uniform(0.0, 2 * math.pi)
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.ang_vel: float = 0.0

        # energy / life
        self.energy: float = energy
        self.age: float = 0.0
        self.alive: bool = True

        # traits
        self.trait_fov_deg: float = fov_deg
        self.trait_range: float = rng_len
        self.trait_thrust_eff: float = thrust_eff
        self.trait_metabolism_eff: float = metabolism_eff

        # sex
        self.sex: str = sex if sex in ("M", "F") else ("M" if random.random() < 0.5 else "F")

        # brain
        self.brain: Brain = brain if brain is not None else Brain()
        self.last_inputs = None
        self.last_outputs = None

        # sleep / dreams
        self.awake: bool = True
        self.sleep_pressure: float = 0.0
        self.dream_timer: float = 0.0
        self.memory: deque = deque(maxlen=MEMORY_BUFFER_SIZE)

        # home / nurture hooks
        self.home_pos: Optional[Tuple[float, float]] = None

        # visuals
        self.trail: deque = deque(maxlen=MASTER_TRAIL_POINTS)
        self.last_seen_target = None

    # ------------------------------------------------------------------ #
    # Core dynamics
    # ------------------------------------------------------------------ #

    def sense(self, foods) -> tuple[float, float]:
        """
        Cast a cone of SENSOR_RAYS rays within FOV and compute
        left/right sensor activations based on food hits.
        """
        if not foods:
            return 0.0, 0.0

        left_val = 0.0
        right_val = 0.0

        # Use current trait FOV/range
        fov_rad = math.radians(self.trait_fov_deg)
        max_dist = self.trait_range

        hits = raycast_cone(
            self.x,
            self.y,
            self.angle,
            fov_rad,
            max_dist,
            SENSOR_RAYS,
            foods,
        )

        for hit_angle, dist in hits:
            if dist <= 0.0 or dist > max_dist:
                continue
            # nearer = stronger
            strength = max(0.0, 1.0 - dist / max_dist)
            if hit_angle < 0:
                left_val = max(left_val, strength)
            else:
                right_val = max(right_val, strength)

        return left_val, right_val

    def physics_step(self, dt: float, thrust_norm: float, turn_norm: float) -> float:
        """
        Integrate physics for dt seconds.
        Returns speed magnitude after the update.
        """
        # thrust_norm in [0,1]; scale by trait + BASE_THRUST
        thrust = thrust_norm * BASE_THRUST * self.trait_thrust_eff

        # forward acceleration
        ax = math.cos(self.angle) * thrust
        ay = math.sin(self.angle) * thrust

        # apply drag
        ax -= LIN_DRAG * self.vx
        ay -= LIN_DRAG * self.vy

        # update velocity
        self.vx += ax * dt
        self.vy += ay * dt

        # clamp speed
        speed = math.hypot(self.vx, self.vy)
        if speed > MAX_SPEED:
            scale = MAX_SPEED / max(speed, 1e-6)
            self.vx *= scale
            self.vy *= scale
            speed = MAX_SPEED

        # angular dynamics
        torque = turn_norm * MAX_TURN_TORQUE
        ang_acc = torque - ANG_DRAG * self.ang_vel
        self.ang_vel += ang_acc * dt
        self.angle = (self.angle + self.ang_vel * dt) % (2 * math.pi)

        # integrate position with wrap-around (torus)
        self.x = (self.x + self.vx * dt) % WORLD_WIDTH
        self.y = (self.y + self.vy * dt) % WORLD_HEIGHT

        # update trail
        self.trail.append((self.x, self.y))

        return speed

    def metabolism_cost(self, speed: float, brain_tick: bool = True) -> float:
        """
        Energy cost per second.
        """
        cost = METABOLISM_BASE * self.trait_metabolism_eff
        cost += METABOLISM_SPEED_COEF * speed * self.trait_metabolism_eff
        if brain_tick:
            cost += METABOLISM_BRAIN_COEF
        return cost

    # ------------------------------------------------------------------ #
    # Developmental scaling for learning
    # ------------------------------------------------------------------ #

    def _dev_learning_scale(self) -> float:
        """
        Younger organisms learn more; older ones less (sigmoid-ish).
        """
        a = self.age / max(DEV_LEARNING_AGE_HALF, 1e-6)
        base = 1.0 / (1.0 + a)  # decays from 1 -> ~0 as age grows
        return DEV_LEARNING_MIN + (1.0 - DEV_LEARNING_MIN) * base

    def _dev_scaled_reward(self, reward: float) -> float:
        return reward * self._dev_learning_scale()

    # ------------------------------------------------------------------ #
    # Sleep / dreams
    # ------------------------------------------------------------------ #

    def _update_sleep_pressure(self, dt: float, env) -> None:
        """
        Increase sleep pressure while awake.
        env.day_night_factor in [0,1]; near 0 = night, 1 = day.
        """
        if not self.awake:
            return

        self.sleep_pressure += SLEEP_PRESSURE_RATE * dt
        self.sleep_pressure = min(1.5, self.sleep_pressure)

        if env is None:
            circadian = 1.0
        else:
            circadian = 1.0 - getattr(env, "day_night_factor", 0.0)  # more likely to sleep in dark

        drive = self.sleep_pressure * (
            SLEEP_NIGHT_WEIGHT * circadian + (1.0 - SLEEP_NIGHT_WEIGHT)
        )
        if drive > SLEEP_MIN_PRESSURE:
            self._enter_sleep()

    def _enter_sleep(self) -> None:
        if not self.awake:
            return
        self.awake = False
        # dream length 2–6 s depending on how tired we are
        self.dream_timer = 2.0 + 4.0 * min(1.0, self.sleep_pressure)

    def _sleep_step(self, dt: float, env) -> bool:
        """
        Called instead of normal awake step when organism is sleeping.
        No movement, reduced metabolism, and dream replay learning.
        Returns ate=False always (no food while sleeping).
        """
        if self.energy <= 0.0:
            self.alive = False
            return False

        # cheaper metabolism
        sleep_cost = self.metabolism_cost(speed=0.0, brain_tick=False) * SLEEP_METABOLISM_FACTOR
        self.energy -= sleep_cost * dt
        self.age += dt

        # dream replay: multiple mini-steps per second of sleep
        dream_steps = int(DREAM_STEPS_PER_SEC * dt)
        for _ in range(dream_steps):
            if not self.memory:
                break
            x_vec, action_vec, reward = random.choice(self.memory)
            noisy_x = x_vec + np.random.normal(0.0, 0.05, size=x_vec.shape)
            # forward without moving body; ignore outputs
            self.brain.forward(noisy_x)
            self.brain.apply_plasticity(self._dev_scaled_reward(reward))

        # recover sleep pressure
        self.sleep_pressure = max(0.0, self.sleep_pressure - SLEEP_RECOVERY_RATE * dt)
        self.dream_timer -= dt

        if self.dream_timer <= 0.0 or self.energy <= 0.0:
            self.awake = True

        if self.energy <= 0.0:
            self.alive = False

        return False

    # ------------------------------------------------------------------ #
    # Main step
    # ------------------------------------------------------------------ #

    def step(self, dt: float, foods, rng: random.Random, env=None) -> bool:
        """
        Advance organism by dt seconds.

        :param dt:   timestep in seconds.
        :param foods: list of Food objects.
        :param rng:  random.Random instance.
        :param env:  Environment (for day/night factor, etc.).
        :return: True if ate this step, False otherwise.
        """
        if not self.alive:
            return False

        energy_before = self.energy

        # If sleeping, run sleep logic
        if not self.awake:
            return self._sleep_step(dt, env)

        # ===== SENSE =====
        left, right = self.sense(foods)

        # ===== BRAIN I/O =====
        energy_norm = max(0.0, min(1.0, self.energy / (REPRODUCTION_THRESHOLD + 1.0)))
        speed_now = math.hypot(self.vx, self.vy)
        speed_norm = min(1.0, speed_now / MAX_SPEED)
        age_norm = min(1.0, self.age / MAX_AGE)
        x_vec = np.array(
            [left, right, energy_norm, speed_norm, age_norm, 1.0],
            dtype=float,
        )

        turn_out, thrust_out = self.brain.forward(x_vec)

        # record inputs/outputs before reflex shaping
        self.last_inputs = (left, right, energy_norm, speed_norm, age_norm)

        # --- reflex assist (steer toward stronger signal) ---
        conf = max(left, right)
        if abs(left - right) < 0.08:
            turn_out *= 0.4
        thrust_out = max(thrust_out, min(1.0, 0.25 + 0.75 * conf))
        steer = (right - left)
        turn_out = 0.7 * turn_out + 0.3 * steer

        self.last_outputs = (turn_out, thrust_out)

        # ===== PHYSICS =====
        speed = self.physics_step(dt, thrust_out, turn_out)

        # ===== EAT =====
        ate = False
        for f in list(foods):
            dx, dy = torus_delta(self.x, self.y, f.x, f.y)
            if dx * dx + dy * dy <= EAT_RADIUS * EAT_RADIUS:
                self.energy += FOOD_ENERGY
                foods.remove(f)
                ate = True
                break

        # ===== ENERGY UPDATE =====
        self.energy -= self.metabolism_cost(speed, brain_tick=True) * dt

        # senescence
        if self.age > MAX_AGE:
            self.energy -= 0.02 * (self.age - MAX_AGE) * dt

        self.age += dt
        if self.energy <= 0.0:
            self.alive = False

        # ===== REWARD & LEARNING =====
        reward = self.energy - energy_before
        reward = max(-1.0, min(1.0, reward))

        # log experience for later dreaming
        self.memory.append(
            (
                x_vec.copy(),
                np.array([turn_out, thrust_out], dtype=float),
                reward,
            )
        )

        # online plasticity
        self.brain.apply_plasticity(self._dev_scaled_reward(reward))

        # sleep pressure update
        self._update_sleep_pressure(dt, env)

        return ate

    # ------------------------------------------------------------------ #
    # Reproduction
    # ------------------------------------------------------------------ #

    def can_reproduce(self) -> bool:
        return self.energy >= REPRODUCTION_THRESHOLD and self.alive

    def reproduce_asexual(self, rng: random.Random) -> "Organism":
        """
        Asexual reproduction: single parent buds off a mutated child.
        """
        child_energy = self.energy * CHILD_TAKE
        self.energy *= PARENT_KEEP

        child_brain = self.brain.copy_mutated()

        # 50% chance: mirror L/R input channels (indices 0 and 1)
        if rng.random() < 0.5:
            child_brain.w_in[[0, 1], :] = child_brain.w_in[[1, 0], :]

        fov_deg, rng_len, thrust_eff, meta_eff = inherit_traits(self, rng)
        child = Organism(
            x=(self.x + rng.uniform(-4, 4)) % WORLD_WIDTH,
            y=(self.y + rng.uniform(-4, 4)) % WORLD_HEIGHT,
            angle=(self.angle + rng.uniform(-0.25, 0.25)) % (2 * math.pi),
            energy=child_energy,
            brain=child_brain,
            gen=self.gen + 1,
            fov_deg=fov_deg,
            rng_len=rng_len,
            thrust_eff=thrust_eff,
            metabolism_eff=meta_eff,
            sex=None,  # random sex
            parents=(self.id,),
        )
        # register dependency (nature hook)
        self.dependents.add(child.id)
        return child

    @staticmethod
    def reproduce_sexual(
        parent_a: "Organism",
        parent_b: "Organism",
        rng: random.Random,
    ) -> Optional["Organism"]:
        """
        Sexual reproduction: combine traits & brains of two parents.
        Returns child or None if parents cannot pay energy cost.
        """
        if not (parent_a.alive and parent_b.alive):
            return None
        if parent_a.energy < REPRODUCTION_THRESHOLD or parent_b.energy < REPRODUCTION_THRESHOLD:
            return None

        # require opposite sex
        if parent_a.sex == parent_b.sex:
            return None

        # split energy
        ea = parent_a.energy * CHILD_TAKE
        eb = parent_b.energy * CHILD_TAKE
        parent_a.energy *= PARENT_KEEP
        parent_b.energy *= PARENT_KEEP
        child_energy = ea + eb

        # Brain recombination: simple averaging + mutation
        with torch.no_grad():
            w_in = 0.5 * (parent_a.brain.w_in + parent_b.brain.w_in)
            w_rec = 0.5 * (parent_a.brain.w_rec + parent_b.brain.w_rec)
            b_h = 0.5 * (parent_a.brain.b_h + parent_b.brain.b_h)
            w_out = 0.5 * (parent_a.brain.w_out + parent_b.brain.w_out)
            b_out = 0.5 * (parent_a.brain.b_out + parent_b.brain.b_out)

        child_brain = Brain(params=(w_in, w_rec, b_h, w_out, b_out))
        child_brain = child_brain.copy_mutated()

        # 50% swap LR channels for symmetry
        if rng.random() < 0.5:
            child_brain.w_in[[0, 1], :] = child_brain.w_in[[1, 0], :]

        # Trait inheritance: sample from parents then mutate
        fov = mutate_val(
            rng.choice([parent_a.trait_fov_deg, parent_b.trait_fov_deg]),
            FOV_MIN,
            FOV_MAX,
            rng,
        )
        rng_len = mutate_val(
            rng.choice([parent_a.trait_range, parent_b.trait_range]),
            RANGE_MIN,
            RANGE_MAX,
            rng,
        )
        thrust_eff = mutate_val(
            rng.choice([parent_a.trait_thrust_eff, parent_b.trait_thrust_eff]),
            THRUST_MIN,
            THRUST_MAX,
            rng,
        )
        meta_eff = mutate_val(
            rng.choice([parent_a.trait_metabolism_eff, parent_b.trait_metabolism_eff]),
            META_MIN,
            META_MAX,
            rng,
        )

        # place child between parents
        cx = (parent_a.x + parent_b.x) * 0.5
        cy = (parent_a.y + parent_b.y) * 0.5

        child = Organism(
            x=cx % WORLD_WIDTH,
            y=cy % WORLD_HEIGHT,
            angle=rng.uniform(0.0, 2 * math.pi),
            energy=child_energy,
            brain=child_brain,
            gen=max(parent_a.gen, parent_b.gen) + 1,
            fov_deg=fov,
            rng_len=rng_len,
            thrust_eff=thrust_eff,
            metabolism_eff=meta_eff,
            sex=None,  # random sex
            parents=(parent_a.id, parent_b.id),
        )

        # register nurture links
        parent_a.dependents.add(child.id)
        parent_b.dependents.add(child.id)
        return child

    # ------------------------------------------------------------------ #
    # Homes / nurture stubs
    # ------------------------------------------------------------------ #

    def has_home(self) -> bool:
        return self.home_pos is not None

    def maybe_build_home(self) -> None:
        """
        Simple heuristic: if allowed, no home yet, and sufficient energy, build one.
        """
        if not CAN_BUILD_HOMES:
            return
        if self.home_pos is not None:
            return
        if self.energy < REPRODUCTION_THRESHOLD + HOME_BUILD_ENERGY_COST:
            return
        # pay cost and establish home at current location
        self.energy -= HOME_BUILD_ENERGY_COST
        self.home_pos = (self.x, self.y)

    def is_child_dependent(self, child: "Organism") -> bool:
        return child.age < CHILD_DEPENDENCY_AGE

    def nurture_child(self, child: "Organism") -> None:
        """
        Very simple parental care: if near a dependent child and we have surplus
        energy, donate a small fraction of our surplus.
        """
        if not (self.alive and child.alive):
            return
        if child.id not in self.dependents:
            return
        if not self.is_child_dependent(child):
            return

        dx, dy = torus_delta(self.x, self.y, child.x, child.y)
        dist2 = dx * dx + dy * dy
        if dist2 > HOME_RADIUS * HOME_RADIUS:
            return

        surplus = max(0.0, self.energy - REPRODUCTION_THRESHOLD)
        if surplus <= 0.0:
            return

        transfer = surplus * PARENT_FEED_SHARE
        self.energy -= transfer
        child.energy += transfer
