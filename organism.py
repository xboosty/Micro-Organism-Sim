import math, random
import numpy as np
from collections import deque
from brain import Brain
from vision import torus_delta, raycast_cone
from genetics import inherit_traits
from config import (
    WORLD_WIDTH, WORLD_HEIGHT,
    BASE_THRUST, MAX_TURN_TORQUE, LIN_DRAG, ANG_DRAG, MAX_SPEED,
    SENSOR_RANGE_DEFAULT, SENSOR_FOV_DEG_DEFAULT, SENSOR_RAYS,
    START_ENERGY, METABOLISM_BASE, METABOLISM_SPEED_COEF, METABOLISM_BRAIN_COEF,
    FOOD_ENERGY, EAT_RADIUS,
    REPRODUCTION_THRESHOLD, PARENT_KEEP, CHILD_TAKE,
    MAX_AGE,
    MASTER_TRAIL_POINTS
)

class Organism:
    _next_id = 0

    def __init__(self, x, y, angle=None, energy=START_ENERGY, brain=None, gen=0,
                 fov_deg=SENSOR_FOV_DEG_DEFAULT, rng_len=SENSOR_RANGE_DEFAULT,
                 thrust_eff=1.0, metabolism_eff=1.0):
        self.id = Organism._next_id; Organism._next_id += 1
        self.x = x; self.y = y
        self.vx = 0.0; self.vy = 0.0
        self.angle = random.uniform(0, 2*math.pi) if angle is None else angle
        self.ang_vel = 0.0
        self.energy = energy
        self.brain = Brain() if brain is None else brain
        self.gen = gen
        self.age = 0.0
        self.alive = True

        # heritable traits
        self.trait_fov_deg = fov_deg
        self.trait_range = rng_len
        self.trait_thrust_eff = thrust_eff
        self.trait_metabolism_eff = metabolism_eff

        # debug memory
        self.last_seen_target = None
        self.last_inputs = None
        self.last_outputs = None

        # pretty: short trail
        self.trail = deque(maxlen=MASTER_TRAIL_POINTS)

    def sense(self, foods):
        fov_rad = math.radians(self.trait_fov_deg)
        left, right, nearest = raycast_cone(self, foods, fov_rad, self.trait_range, SENSOR_RAYS)
        self.last_seen_target = nearest
        return left, right

    def physics_step(self, dt, thrust_norm, torque_norm):
        # torque -> angular acceleration with clamp + angular drag
        torque = max(-1.0, min(1.0, torque_norm)) * MAX_TURN_TORQUE
        ang_acc = torque - ANG_DRAG * self.ang_vel
        self.ang_vel += ang_acc * dt
        self.ang_vel = max(-6.0, min(6.0, self.ang_vel))
        self.angle = (self.angle + self.ang_vel * dt) % (2*math.pi)

        # thrust forward with drag and speed clamp
        thrust = max(0.0, min(1.0, thrust_norm)) * BASE_THRUST * self.trait_thrust_eff
        ax = math.cos(self.angle) * thrust - LIN_DRAG * self.vx
        ay = math.sin(self.angle) * thrust - LIN_DRAG * self.vy
        self.vx += ax * dt; self.vy += ay * dt

        speed = (self.vx**2 + self.vy**2)**0.5
        if speed > MAX_SPEED:
            scale = MAX_SPEED / max(1e-6, speed)
            self.vx *= scale; self.vy *= scale
            speed = MAX_SPEED

        # integrate position with torus wrap
        self.x = (self.x + self.vx * dt) % WORLD_WIDTH
        self.y = (self.y + self.vy * dt) % WORLD_HEIGHT

        # trail for pretty (store current pos)
        self.trail.append((self.x, self.y))

        return speed

    def metabolism_cost(self, speed, brain_tick=True):
        cost = (METABOLISM_BASE * self.trait_metabolism_eff)
        cost += METABOLISM_SPEED_COEF * speed
        if brain_tick:
            cost += METABOLISM_BRAIN_COEF
        return cost

    def step(self, dt, foods, rng):
        # SENSE
        left, right = self.sense(foods)

        # BRAIN I/O
        energy_norm = max(0.0, min(1.0, self.energy / (REPRODUCTION_THRESHOLD + 1.0)))
        speed_norm = min(1.0, (self.vx**2 + self.vy**2)**0.5 / MAX_SPEED)
        age_norm = min(1.0, self.age / MAX_AGE)
        x = np.array([left, right, energy_norm, speed_norm, age_norm, 1.0], dtype=float)
        turn_out, thrust_out = self.brain.forward(x)

        # record inputs/outputs before any reflex shaping
        self.last_inputs = (left, right, energy_norm, speed_norm, age_norm)

        # === Reflex assist (only when vision confidence is high) ===
        conf = max(left, right)
        if abs(left - right) < 0.08:
            turn_out *= 0.4
        thrust_out = max(thrust_out, min(1.0, 0.25 + 0.75 * conf))
        steer = (right - left)
        turn_out = 0.7 * turn_out + 0.3 * steer

        self.last_outputs = (turn_out, thrust_out)

        # PHYSICS
        speed = self.physics_step(dt, thrust_out, turn_out)

        # EAT
        ate = False
        for f in list(foods):
            dx, dy = torus_delta(self.x, self.y, f.x, f.y)
            if dx*dx + dy*dy <= EAT_RADIUS*EAT_RADIUS:
                self.energy += FOOD_ENERGY
                foods.remove(f)
                ate = True
                break

        # ENERGY
        self.energy -= self.metabolism_cost(speed) * dt

        # senescence
        if self.age > MAX_AGE:
            self.energy -= 0.02 * (self.age - MAX_AGE) * dt

        self.age += dt
        if self.energy <= 0.0:
            self.alive = False

        return ate

    def can_reproduce(self):
        return self.energy >= REPRODUCTION_THRESHOLD

    def reproduce(self, rng):
        # Split energy and inherit+mutate brain and traits
        child_energy = self.energy * CHILD_TAKE
        self.energy *= PARENT_KEEP

        child_brain = self.brain.copy_mutated()

        # 50% chance: mirror L/R channels to encourage both handednesses
        import numpy as np, random as pyrand
        if pyrand.random() < 0.5:
            child_brain.w1[:, [0, 1]] = child_brain.w1[:, [1, 0]]

        fov_deg, rng_len, thrust_eff, meta_eff = inherit_traits(self, rng)
        child = Organism(
            x=(self.x + rng.uniform(-4,4)) % WORLD_WIDTH,
            y=(self.y + rng.uniform(-4,4)) % WORLD_HEIGHT,
            angle=(self.angle + rng.uniform(-0.25,0.25)) % (2*math.pi),
            energy=child_energy,
            brain=child_brain,
            gen=self.gen + 1,
            fov_deg=fov_deg, rng_len=rng_len,
            thrust_eff=thrust_eff, metabolism_eff=meta_eff
        )
        return child
