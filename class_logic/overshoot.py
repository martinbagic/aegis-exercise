import numpy as np


class Overshoot:
    """Class for deciding which individuals to eliminate when overcrowded"""

    def __init__(self, OVERSHOOT_EVENT, MAX_POPULATION_SIZE, CLIFF_SURVIVORSHIP):
        self.MAX_POPULATION_SIZE = MAX_POPULATION_SIZE
        self.CLIFF_SURVIVORSHIP = CLIFF_SURVIVORSHIP
        self.func = {
            "treadmill_random": self._treadmill_random,
            "treadmill_boomer": self._treadmill_boomer,
            "treadmill_zoomer": self._treadmill_zoomer,
            "cliff": self._cliff,
            "starvation": self._starvation,
        }[OVERSHOOT_EVENT]

        self.consecutive_overshoot_n = 0  # For starvation mode

    def __call__(self, n):
        """The exposed function for calling"""
        if n <= self.MAX_POPULATION_SIZE:
            self.consecutive_overshoot_n = 0
            return np.zeros(n, bool)
        else:
            self.consecutive_overshoot_n += 1
            return self.func(n)

    def _starvation(self, n):
        """Let starved individuals die"""
        if n > self.MAX_POPULATION_SIZE:
            surv_probability = 0.95 ** self.consecutive_overshoot_n
            random_probabilities = np.random.rand(n)
            mask = random_probabilities > surv_probability
        return mask

    def _treadmill_random(self, n):
        """Kill some extra individuals randomly"""
        indices = np.random.choice(n, n - self.MAX_POPULATION_SIZE, replace=False)
        mask = np.zeros(n, bool)
        mask[indices] = True
        return mask

    def _cliff(self, n):
        """Kill all but random few"""
        indices = np.random.choice(
            n, int(self.MAX_POPULATION_SIZE * self.CLIFF_SURVIVORSHIP), replace=False
        )
        mask = np.ones(n, bool)
        mask[indices] = False
        return mask

    def _treadmill_boomer(self, n):
        """Kill the oldest. Let youngest live."""
        mask = np.ones(n, bool)
        mask[-self.MAX_POPULATION_SIZE :] = False
        return mask

    def _treadmill_zoomer(self, n):
        """Kill the youngest. Let oldest live."""
        mask = np.ones(n, bool)
        mask[: self.MAX_POPULATION_SIZE] = False
        return mask
