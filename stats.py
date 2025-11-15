"""
stats.py

Lightweight analytics helpers for the Micro-Organism Simulation.

These functions are pure and side-effect-free; they just inspect a World
instance and return dictionaries / aggregates you can log, print, or plot.
"""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, Any, Tuple, List, Optional

from world import World
from organism import Organism


def _safe_mean(values: List[float], default: float = 0.0) -> float:
    return mean(values) if values else default


def organism_basic_stats(orgs: List[Organism]) -> Dict[str, Any]:
    """
    Compute basic statistics over a list of organisms.
    """
    if not orgs:
        return {
            "count": 0,
            "mean_age": 0.0,
            "max_age": 0.0,
            "mean_energy": 0.0,
            "max_energy": 0.0,
        }

    ages = [o.age for o in orgs]
    energies = [o.energy for o in orgs]

    return {
        "count": len(orgs),
        "mean_age": _safe_mean(ages),
        "max_age": max(ages),
        "mean_energy": _safe_mean(energies),
        "max_energy": max(energies),
    }


def organism_trait_stats(orgs: List[Organism]) -> Dict[str, Any]:
    """
    Compute mean and spread of key traits over all organisms.
    """
    if not orgs:
        return {}

    fovs = [o.trait_fov_deg for o in orgs]
    ranges = [o.trait_range for o in orgs]
    thrusts = [o.trait_thrust_eff for o in orgs]
    metas = [o.trait_metabolism_eff for o in orgs]
    gens = [o.gen for o in orgs]

    return {
        "mean_fov": _safe_mean(fovs),
        "min_fov": min(fovs),
        "max_fov": max(fovs),
        "mean_range": _safe_mean(ranges),
        "min_range": min(ranges),
        "max_range": max(ranges),
        "mean_thrust_eff": _safe_mean(thrusts),
        "min_thrust_eff": min(thrusts),
        "max_thrust_eff": max(thrusts),
        "mean_meta_eff": _safe_mean(metas),
        "min_meta_eff": min(metas),
        "max_meta_eff": max(metas),
        "mean_gen": _safe_mean(gens),
        "max_gen": max(gens),
    }


def sex_ratio(orgs: List[Organism]) -> Dict[str, Any]:
    """
    Count males vs females in the population.
    """
    c = Counter(o.sex for o in orgs)
    total = sum(c.values()) or 1
    return {
        "M": c.get("M", 0),
        "F": c.get("F", 0),
        "ratio_M": c.get("M", 0) / total,
        "ratio_F": c.get("F", 0) / total,
    }


def dependency_stats(orgs: List[Organism]) -> Dict[str, Any]:
    """
    How many organisms are parents / children in nurture relationships.
    """
    parent_count = sum(1 for o in orgs if o.dependents)
    total_dependents = sum(len(o.dependents) for o in orgs)
    return {
        "parents_with_dependents": parent_count,
        "total_dependents_links": total_dependents,
    }


def home_stats(orgs: List[Organism]) -> Dict[str, Any]:
    """
    Simple stats on home-building behavior.
    """
    with_home = [o for o in orgs if o.home_pos is not None]
    return {
        "homes_built": len(with_home),
    }


def world_snapshot(world: World) -> Dict[str, Any]:
    """
    Take a one-shot snapshot of world-level stats for logging or plotting.

    Returns a nested dictionary that you can serialize to JSON, log, or
    inspect interactively.
    """
    orgs = world.orgs
    env = world.env

    basic = organism_basic_stats(orgs)
    traits = organism_trait_stats(orgs)
    sexes = sex_ratio(orgs)
    deps = dependency_stats(orgs)
    homes = home_stats(orgs)

    snapshot: Dict[str, Any] = {
        "time": world.time,
        "population": len(orgs),
        "food_count": len(world.foods),
        "births": world.births,
        "deaths": world.deaths,
        "generation_high": world.generation_high,
        "organisms": {
            **basic,
            **traits,
            "sex": sexes,
            "nurture": deps,
            "homes": homes,
        },
        "environment": {
            "day_night_factor": env.day_night_factor,
            "precipitation": env.precipitation,
            "global_growth_rate": env.global_growth_rate(),
        },
    }

    return snapshot
