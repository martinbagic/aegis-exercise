import numpy as np

from aegis.panconfiguration import pan


class Environment:
    """Functional environmental map class"""

    def __init__(self, gstruc, ENVIRONMENT_CHANGE_RATE):

        if ENVIRONMENT_CHANGE_RATE == 0:
            self.dummy = True
        else:
            self.dummy = False
            self.map_ = np.zeros(gstruc.shape, bool)
            self.ENVIRONMENT_CHANGE_RATE = ENVIRONMENT_CHANGE_RATE

    def __call__(self, genomes):
        """Return the genomes reinterpreted in the current environment"""
        return genomes if self.dummy else np.logical_xor(self.map_, genomes)

    def evolve(self):
        """Modify the environmental map"""
        if self.dummy or pan.skip(self.ENVIRONMENT_CHANGE_RATE):
            return

        chromatid = pan.rng.integers(self.map_.shape[0])
        locus = pan.rng.integers(self.map_.shape[1])
        bit = pan.rng.integers(self.map_.shape[2])

        self.map_[chromatid, locus, bit] = ~self.map_[chromatid, locus, bit]
