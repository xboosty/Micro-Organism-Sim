import math
from typing import Optional, Tuple

import numpy as np
import torch

from config import (
    BRAIN_INPUT_SIZE,
    BRAIN_HIDDEN,
    BRAIN_OUTPUT_SIZE,
    MUTATION_RATE,
    MUTATION_SCALE,
    BRAIN_PLASTICITY_RATE,
    BRAIN_PLASTICITY_DECAY,
)

# Use GPU if available (RTX 3080 friendly), otherwise fall back to CPU.
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Brain:
    """
    Tiny recurrent neural controller with CUDA support and reward-modulated plasticity.

    - Parameters (weights, biases, state) live on DEVICE (cuda if available).
    - Recurrent hidden state h_t gives per-organism memory.
    - Within-lifetime learning via reward-modulated Hebbian updates on W_rec.
    - Evolution across generations handled via copy_mutated().
    """

    def __init__(
        self,
        in_size: int = BRAIN_INPUT_SIZE,
        hidden: int = BRAIN_HIDDEN,
        out_size: int = BRAIN_OUTPUT_SIZE,
        params: Optional[Tuple[torch.Tensor, ...]] = None,
        device: Optional[torch.device] = None,
    ) -> None:
        """
        Initialize a new Brain.

        :param in_size:  Input dimensionality.
        :param hidden:   Number of hidden / recurrent units.
        :param out_size: Output dimensionality.
        :param params:   Optional tuple of pre-defined parameters
                         (w_in, w_rec, b_h, w_out, b_out).
        :param device:   Torch device to place tensors on. Defaults to global DEVICE.
        """
        self.device = device if device is not None else DEVICE

        if params is None:
            # Randomly initialise parameters
            self.w_in = torch.randn(hidden, in_size, device=self.device) * 0.6
            self.w_rec = torch.randn(hidden, hidden, device=self.device) * 0.2
            self.b_h = torch.zeros(hidden, device=self.device)

            self.w_out = torch.randn(out_size, hidden, device=self.device) * 0.6
            self.b_out = torch.zeros(out_size, device=self.device)
        else:
            self.w_in, self.w_rec, self.b_h, self.w_out, self.b_out = [
                p.to(self.device) for p in params
            ]

        # Recurrent hidden state (memory), 1D [hidden]
        self.h = torch.zeros(BRAIN_HIDDEN, device=self.device)

        # Pre/post states for plasticity
        self._last_pre_h = torch.zeros_like(self.h)
        self._last_post_h = torch.zeros_like(self.h)

    # --------------------------------------------------------------------- #
    # Core API
    # --------------------------------------------------------------------- #

    def reset_state(self) -> None:
        """Reset the recurrent hidden state (e.g. on birth/world reset)."""
        self.h.zero_()
        self._last_pre_h.zero_()
        self._last_post_h.zero_()

    def forward(self, x: np.ndarray) -> Tuple[float, float]:
        """
        Single control step.

        :param x: NumPy input vector of shape (in_size,).
        :return: (turn_torque_norm in [-1, 1], thrust_norm in [0, 1]).
        """
        # Convert NumPy -> torch on correct device
        x_t = torch.as_tensor(x, dtype=torch.float32, device=self.device)

        # Store previous state for plasticity
        self._last_pre_h = self.h.clone()

        # Recurrent update: h_t = tanh(W_in x + W_rec h_{t-1} + b)
        h_lin = torch.matmul(self.w_in, x_t) + torch.matmul(self.w_rec, self.h) + self.b_h
        self.h = torch.tanh(h_lin)

        # Store post state
        self._last_post_h = self.h.clone()

        # Output layer: o = tanh(W_out h + b)
        o = torch.tanh(torch.matmul(self.w_out, self.h) + self.b_out)

        # Turn is in [-1, 1], thrust is mapped from [-1, 1] -> [0, 1]
        turn_raw = float(o[0].item())
        thrust_raw = float(o[1].item())
        thrust_norm = (thrust_raw + 1.0) * 0.5

        return turn_raw, thrust_norm

    def apply_plasticity(self, reward: float) -> None:
        """
        Reward-modulated Hebbian plasticity on recurrent weights.

        ΔW_rec ∝ reward * post * pre^T - decay * W_rec

        :param reward: Scalar reward signal. Positive -> strengthen patterns that
                       produced it; negative -> weaken them. Typically clipped.
        """
        # Weight decay to keep dynamics bounded
        self.w_rec.mul_(1.0 - BRAIN_PLASTICITY_DECAY)

        if reward == 0.0:
            return

        # Small learning step scaled by reward
        reward_f = float(reward)
        eta = BRAIN_PLASTICITY_RATE * reward_f

        # post: [hidden], pre: [hidden]
        post = self._last_post_h
        pre = self._last_pre_h

        # Outer product post (rows) x pre (cols) -> [hidden, hidden]
        dw = eta * torch.outer(post, pre)
        self.w_rec.add_(dw)

    # --------------------------------------------------------------------- #
    # Evolutionary mutation
    # --------------------------------------------------------------------- #

    def _mutate_tensor(self, t: torch.Tensor) -> torch.Tensor:
        """
        Apply in-place evolutionary mutation to a tensor and return it.

        Each element is mutated with probability MUTATION_RATE by adding
        Gaussian noise with std MUTATION_SCALE.
        """
        if MUTATION_RATE <= 0.0:
            return t

        # Create Bernoulli mask
        mask = torch.rand_like(t, device=self.device) < MUTATION_RATE
        if mask.any():
            noise = torch.randn_like(t, device=self.device) * MUTATION_SCALE
            t = t + noise * mask  # create new tensor so we don't accidentally share
        return t

    def copy_mutated(self) -> "Brain":
        """
        Copy this brain and apply evolutionary mutation to all parameters.

        This is the across-generations adaptation (evolution).
        Within-lifetime adaptation happens via apply_plasticity().
        """
        w_in = self._mutate_tensor(self.w_in.clone())
        w_rec = self._mutate_tensor(self.w_rec.clone())
        b_h = self._mutate_tensor(self.b_h.clone())
        w_out = self._mutate_tensor(self.w_out.clone())
        b_out = self._mutate_tensor(self.b_out.clone())

        child = Brain(
            in_size=w_in.shape[1],
            hidden=w_in.shape[0],
            out_size=w_out.shape[0],
            params=(w_in, w_rec, b_h, w_out, b_out),
            device=self.device,
        )
        child.reset_state()
        return child

    # --------------------------------------------------------------------- #
    # Utility / Introspection
    # --------------------------------------------------------------------- #

    def to(self, device: torch.device) -> "Brain":
        """
        Move this brain's parameters and state to a new device (cpu/cuda).
        """
        self.device = device
        self.w_in = self.w_in.to(device)
        self.w_rec = self.w_rec.to(device)
        self.b_h = self.b_h.to(device)
        self.w_out = self.w_out.to(device)
        self.b_out = self.b_out.to(device)
        self.h = self.h.to(device)
        self._last_pre_h = self._last_pre_h.to(device)
        self._last_post_h = self._last_post_h.to(device)
        return self
