import time

class Stats:
    def __init__(self, world, interval=1.0):
        self.world = world
        self.interval = interval
        self._last = time.time()

    def maybe_print(self, master=None):
        now = time.time()
        if now - self._last < self.interval:
            return
        self._last = now

        pop = self.world.population()
        food = len(self.world.foods)
        births = self.world.births
        deaths = self.world.deaths
        fov, rng_len, thr, met = self.world.avg_traits()

        print("\n--- Simulation Status ---")
        print(f"Time: {self.world.time:.1f} s | Pop: {pop} | Food: {food} | Births: {births} | Deaths: {deaths} | MaxGen: {self.world.generation_high}")
        print(f"Avg Traits -> FOV: {fov:.1f}°, Range: {rng_len:.1f}px, ThrustEff: {thr:.2f}x, MetaEff: {met:.2f}x")

        if master is not None:
            lo = master.last_inputs
            lo2 = master.last_outputs
            if lo and lo2:
                l, r, e, s, a = lo
                t, u = lo2
                see_txt = "sees target" if master.last_seen_target else "sees nothing"
                print(f"Master id={master.id} gen={master.gen} {see_txt} | E={master.energy:.2f} | "
                      f"in(L={l:.2f} R={r:.2f} E={e:.2f} S={s:.2f} A={a:.2f}) -> out(turn={t:.2f} thrust={u:.2f})")
