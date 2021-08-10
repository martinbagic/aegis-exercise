import numpy as np


class Envmap:
    """Functional environmental map class"""

    def __init__(self, BITS_PER_LOCUS=None, total_loci=None, ENVMAP_RATE=None):

        if BITS_PER_LOCUS is None and total_loci is None and ENVMAP_RATE is None:
            self.fake = True
        else:
            self.fake = False
            self.map_ = np.zeros((total_loci, BITS_PER_LOCUS), bool)
            self.envmap_rate = ENVMAP_RATE

    def __call__(self, genomes):
        """Return the genomes reinterpreted in the current environment"""
        return genomes if self.fake else np.logical_xor(self.map_, genomes)

    def evolve(self, stage):
        """Modify the environmental map"""
        if self.fake:
            return

        if stage % self.envmap_rate == 0:
            locus = np.random.choice(np.arange(self.map_.shape[0]))
            bit = np.random.choice(np.arange(self.map_.shape[1]))
            self.map_[locus, bit] = ~self.map_[locus, bit]
