import random
from config import (
    FOV_MIN, FOV_MAX, RANGE_MIN, RANGE_MAX,
    THRUST_MIN, THRUST_MAX, META_MIN, META_MAX,
    MUTATION_RATE, MUTATION_SCALE
)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def mutate_val(val, lo, hi, rng, scale=MUTATION_SCALE):
    if rng.random() < MUTATION_RATE:
        val += rng.gauss(0.0, scale * (hi - lo) * 0.05)
    return clamp(val, lo, hi)

def inherit_traits(parent, rng):
    fov = mutate_val(parent.trait_fov_deg, FOV_MIN, FOV_MAX, rng)
    rng_len = mutate_val(parent.trait_range, RANGE_MIN, RANGE_MAX, rng)
    thrust_eff = mutate_val(parent.trait_thrust_eff, THRUST_MIN, THRUST_MAX, rng)
    meta_eff = mutate_val(parent.trait_metabolism_eff, META_MIN, META_MAX, rng)
    return fov, rng_len, thrust_eff, meta_eff
