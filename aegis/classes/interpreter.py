import numpy as np


class Interpreter:

    legal = ("uniform", "exp", "binary", "binary_exp", "binary_switch", "switch")

    """Class for transforming locus bits into gene activities"""

    def __init__(self, BITS_PER_LOCUS, REPR_MODE):
        self.ploidy = {"sexual": 2, "asexual": 1, "diasexual": 2}[REPR_MODE]

        # Parameters for the binary interpreter
        self.binary_weights = 2 ** np.arange(BITS_PER_LOCUS // self.ploidy)[::-1]
        self.binary_max = self.binary_weights.sum()

        # Parameters for the binary switch interpreter
        self.binary_switch_weights = self.binary_weights.copy()
        self.binary_switch_weights[-1] = 0
        self.binary_switch_max = self.binary_switch_weights.sum()

        self.interpreter_map = {
            "uniform": self._uniform,
            "exp": self._exp,
            "binary": self._binary,
            "binary_exp": self._binary_exp,
            "binary_switch": self._binary_switch,
            "switch": self._switch,
        }

    def __call__(self, loci, interpreter_kind):
        """The exposed function for calling"""
        interpreter = self.interpreter_map[interpreter_kind]

        # If diploid, check if homozygous 1
        if self.ploidy == 2:
            loci = np.logical_and(loci[:, :, ::2], loci[:, :, 1::2])

        interpretome = interpreter(loci)

        return interpretome

    def _binary(self, loci):
        """
        Locus is interpreted as a binary number and normalized.
        Applicable to surv and repr traits.
        """
        return loci.dot(self.binary_weights) / self.binary_max

    def _switch(self, loci):
        """
        Locus is evaluated as 0, 1 or randomly evaluated as 0 or 1.
        Applicable to surv and repr traits.
        """
        sums = loci.mean(2)
        rand_values = np.random.random(loci.shape[:-1]) < 0.5
        return np.select(
            [sums == 0, (sums > 0) & (sums < 1), sums == 1], [0, rand_values, 1]
        )

    def _binary_switch(self, loci):
        """
        Binary interpreter with a switch bit which, when 0, sets the value of the locus to 0.
        """
        where_on = loci[:, :, -1] == 1  # Loci which are turned on
        values = np.zeros(loci.shape[:-1], float)  # Default locus value is 0
        values[where_on] = (
            loci[where_on].dot(self.binary_switch_weights) / self.binary_switch_max
        )  # If the locus is turned on, make the value be the binary value
        return values

    def _uniform(self, loci):
        """
        Locus is evaluated as the normalized sum of bits.
        Applicable to surv, repr, neut and muta traits.
        """
        return loci.sum(-1) / loci.shape[-1]

    def _exp(self, loci):
        """
        Locus is evaluated as the sum of bits with exponentially decreasing weights.
        Applicable to muta trait."""
        return 1 / 2 ** np.sum(~loci, axis=1)

    def _binary_exp(self, loci):
        """
        Locus is evaluated as 0.98 to the power of the binary value.
        Applicable to muta trait.
        """
        binary = self._binary(loci)
        return 0.98 ** binary
