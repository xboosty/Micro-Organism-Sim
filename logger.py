"""
Central logging utility for the Micro-Organism Simulation.

Provides:
- Console logging (periodic status output)
- CSV logging (population, births, deaths, food count, weather)
- GPU awareness (logs device = cuda/cpu)

All logging behavior is controlled from config.py (intervals, toggles).
"""

import csv
import os
import time
from typing import Optional

import torch

from config import STATUS_PRINT_INTERVAL


class Logger:
    def __init__(self, log_dir: str = "logs", csv_name: str = "world_log.csv") -> None:
        """
        Initialize logger (creates logs/ directory and CSV file if needed).
        """
        self.log_dir = log_dir
        self.csv_path = os.path.join(self.log_dir, csv_name)

        os.makedirs(self.log_dir, exist_ok=True)

        # Create CSV with headers the first time
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "time_s",
                        "population",
                        "births",
                        "deaths",
                        "foods",
                        "avg_fov",
                        "avg_range",
                        "avg_thrust_eff",
                        "avg_meta_eff",
                        "temp_mid_lat",
                        "precip",
                        "day_night",
                        "cuda",
                    ]
                )

        # last time we printed a console update
        self.last_print_time: float = time.time()

    # ------------------------------------------------------------------ #
    # Console logging
    # ------------------------------------------------------------------ #

    def maybe_print(self, world, now: Optional[float] = None) -> None:
        """
        Print an update to the console if enough time has passed.
        """
        now = time.time() if now is None else now
        if now - self.last_print_time < STATUS_PRINT_INTERVAL:
            return
        self.last_print_time = now

        pop = world.population()
        food_count = len(world.foods)

        # environment info
        env = world.env
        temp = env.temperature_at_y(world.env.time % 1 * 100)  # quick sampling
        precip = env.precipitation
        dayf = env.day_night_factor

        # trait averages
        fov, rng_len, thr, meta = world.avg_traits()

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(
            f"[t={world.time:7.1f}s]  "
            f"pop={pop:4d}  food={food_count:3d}  "
            f"births={world.births:3d} deaths={world.deaths:3d}  "
            f"temp≈{temp:5.1f}°C  precip={precip:.2f}  day={dayf:.2f}  "
            f"FOV={fov:.1f}  range={rng_len:.1f}  thr={thr:.2f}  meta={meta:.2f}  "
            f"[{device}]"
        )

    # ------------------------------------------------------------------ #
    # CSV Logging
    # ------------------------------------------------------------------ #

    def log_csv(self, world) -> None:
        """
        Write a CSV row with world stats.
        """
        env = world.env

        fov, rng_len, thr, meta = world.avg_traits()

        row = [
            world.time,
            world.population(),
            world.births,
            world.deaths,
            len(world.foods),
            fov,
            rng_len,
            thr,
            meta,
            env.temperature_at_y(world.env.time % 1 * 100),
            env.precipitation,
            env.day_night_factor,
            "cuda" if torch.cuda.is_available() else "cpu",
        ]

        with open(self.csv_path, "a", newline="") as f:
            csv.writer(f).writerow(row)

