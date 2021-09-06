import numpy as np

from aegis.panconfiguration import pan


class Interpreter:
    """Class for transforming locus bits into gene activities"""

    def __init__(self, BITS_PER_LOCUS):

        # Parameters for the binary interpreter
        self.binary_weights = 2 ** np.arange(BITS_PER_LOCUS)[::-1]
        self.binary_max = self.binary_weights.sum()

        # Parameters for the binary switch interpreter
        # Switch bits do not add to locus value
        self.binary_switch_weights = self.binary_weights.copy()
        self.binary_switch_weights[-1] = 0  # Switch bit does not add to locus value
        self.binary_switch_max = self.binary_switch_weights.sum()

    def __call__(self, loci, interpreter_kind):
        """The exposed function for calling"""
        interpreter = getattr(self, f"_{interpreter_kind}")

        loci = self._diploid_to_haploid(loci)
        # Now, shape of loci is (population_size, gstruc.length, bits_per_locus)

        interpretome = interpreter(loci)

        return interpretome

    def _diploid_to_haploid(self, loci):
        # Now implied semidominance, but other inheritance modes are possible
        return loci.mean(1)

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
        rand_values = pan.rng.random(loci.shape[:-1]) < 0.5
        return np.select(
            [sums == 0, (sums > 0) & (sums < 1), sums == 1], [0, rand_values, 1]
        )

    def _binary_switch(self, loci):
        """
        If any of the last n bits of an n-ploid population is 0, the locus resolves to 0.
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
        return 0.5 ** np.sum(1 - loci, axis=2)

    def _binary_exp(self, loci):
        """
        Locus is evaluated as 0.98 to the power of the binary value.
        Applicable to muta trait.
        """
        binary = self._binary(loci)
        return 0.98 ** binary
