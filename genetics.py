from __future__ import annotations

import random
from typing import Tuple

from config import (
    MUTATION_RATE,
    MUTATION_SCALE,
    FOV_MIN,
    FOV_MAX,
    RANGE_MIN,
    RANGE_MAX,
    THRUST_MIN,
    THRUST_MAX,
    META_MIN,
    META_MAX,
)


def mutate_val(
    base: float,
    vmin: float,
    vmax: float,
    rng: random.Random,
    rate: float = MUTATION_RATE,
    scale: float = MUTATION_SCALE,
) -> float:
    """
    Mutate a scalar trait value.

    With probability `rate`, add Gaussian noise with std `scale`.
    Result is clamped to [vmin, vmax].
    """
    val = base
    if rng.random() < rate:
        val += rng.gauss(0.0, scale)
    if vmin is not None:
        val = max(vmin, val)
    if vmax is not None:
        val = min(vmax, val)
    return val


def inherit_traits(parent, rng: random.Random) -> Tuple[float, float, float, float]:
    """
    Asexual trait inheritance.

    Child traits are copied from parent and then mutated & clamped
    to the configured bounds.

    Returns:
        (fov_deg, range_len, thrust_eff, metabolism_eff)
    """
    fov = mutate_val(parent.trait_fov_deg, FOV_MIN, FOV_MAX, rng)
    rng_len = mutate_val(parent.trait_range, RANGE_MIN, RANGE_MAX, rng)
    thrust_eff = mutate_val(parent.trait_thrust_eff, THRUST_MIN, THRUST_MAX, rng)
    meta_eff = mutate_val(parent.trait_metabolism_eff, META_MIN, META_MAX, rng)
    return fov, rng_len, thrust_eff, meta_eff
