from aegis.modules.trait import Trait
from aegis.panconfiguration import pan


class Gstruc:
    """Genome structure

    genomes.shape == (population size, length, ploidy, bits_per_locus)
    """

    def __init__(self, params, BITS_PER_LOCUS, REPRODUCTION_MODE):

        self.traits = {name: Trait(name, params) for name in Trait.legal}
        self.evolvable = [trait for trait in self.traits.values() if trait.evolvable]
        self.length = 0

        for trait in self.traits.values():
            trait.start = self.length
            trait.end = self.length + trait.length
            trait.slice = slice(trait.start, trait.end)

            self.length = trait.end

        # Consider ploidy
        self.ploidy = {
            "sexual": 2,
            "asexual": 1,
            "asexual_diploid": 2,
        }[REPRODUCTION_MODE]

        self.bits_per_locus = BITS_PER_LOCUS

        self.shape = (self.ploidy, self.length, self.bits_per_locus)

    def __getitem__(self, name):
        return self.traits[name]

    def initialize_genomes(self, n, headsup=None):

        # Initial genomes with a trait.initial fraction of 1's
        genomes = pan.rng.random(
            size=(n, *self.shape)
        )

        for trait in self.evolvable:
            genomes[:, :, trait.slice] = genomes[:, :, trait.slice] <= trait.initial

        genomes = genomes.astype(bool)

        # Guarantee survival and reproduction values up to a certain age
        if headsup is not None:
            surv_start = self["surv"].start
            repr_start = self["repr"].start
            genomes[:, :, surv_start : surv_start + headsup] = True
            genomes[:, :, repr_start : repr_start + headsup] = True

        return genomes
