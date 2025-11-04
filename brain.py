import numpy as np
from config import MUTATION_RATE, MUTATION_SCALE

# inputs: [left, right, energy, speed_norm, age_norm, bias]
# outputs: [turn_torque_norm (-1..1), thrust_norm (0..1)]
class Brain:
    def __init__(self, in_size=6, hidden=10, out_size=2, rng=None, params=None):
        self.rng = np.random.default_rng() if rng is None else rng
        if params is None:
            self.w1 = self.rng.normal(0, 0.6, (hidden, in_size))
            self.b1 = np.zeros((hidden,))
            self.w2 = self.rng.normal(0, 0.6, (out_size, hidden))
            self.b2 = np.zeros((out_size,))
        else:
            self.w1, self.b1, self.w2, self.b2 = params

    def forward(self, x):
        h = np.tanh(self.w1 @ x + self.b1)
        o = np.tanh(self.w2 @ h + self.b2)
        return float(o[0]), (float(o[1]) + 1.0) * 0.5

    def copy_mutated(self):
        w1, b1, w2, b2 = [np.array(a, copy=True) for a in (self.w1, self.b1, self.w2, self.b2)]
        def mutate(arr):
            mask = (self.rng.random(arr.shape) < MUTATION_RATE)
            arr[mask] += self.rng.normal(0.0, MUTATION_SCALE, arr[mask].shape)
        mutate(w1); mutate(b1); mutate(w2); mutate(b2)
        return Brain(params=(w1, b1, w2, b2), rng=self.rng)
