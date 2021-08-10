import numpy as np

from aegis._deme._config.interpreter import Interpreter
from aegis._deme._config.overshoot import Overshoot
from aegis._deme._config.phenomap import Phenomap
from aegis._deme._config.season import Season
from aegis._deme._config.envmap import Envmap
from aegis._deme._config.gstruc import Gstruc


class Config:
    """Wrapper for deme-specific parameters"""

    def __init__(self, params):

        # Population parameters
        self.MAX_LIFESPAN = params["MAX_LIFESPAN"]
        self.MATURATION_AGE = params["MATURATION_AGE"]
        self.BITS_PER_LOCUS = params["BITS_PER_LOCUS"]
        self.HEADSUP = params["HEADSUP"]
        self.REPR_MODE = params["REPR_MODE"]
        self.MUTATION_RATIO = params["MUTATION_RATIO"]
        self.RECOMBINATION_RATE = params["RECOMBINATION_RATE"]

        # Ecology parameters
        self.MAX_POPULATION_SIZE = params["MAX_POPULATION_SIZE"]
        self.OVERSHOOT_EVENT = params["OVERSHOOT_EVENT"]
        self.DISCRETE_GENERATIONS = params["DISCRETE_GENERATIONS"]
        self.ENVMAP_RATE = params["ENVMAP_RATE"]
        self.PHENOMAP_PLUS = params["PHENOMAP_PLUS"]
        self.CLIFF_SURVIVORSHIP = params["CLIFF_SURVIVORSHIP"]

        # Genome structure
        self.gstruc = Gstruc(params)
        #     traits=[Trait(name, params) for name in PAN.traits]
        # )

        # Simulation variables
        self.max_uid = 0  # ID of the most recently born individual

        # Seasonality
        self.season = Season(DISCRETE_GENERATIONS=self.DISCRETE_GENERATIONS)

        # Interpreters
        self.interpreter = Interpreter(
            BITS_PER_LOCUS=self.BITS_PER_LOCUS,
            REPR_MODE=self.REPR_MODE,
        )

        # Phenomap
        self.phenomap = (
            Phenomap(PHENOMAP_PLUS=self.PHENOMAP_PLUS, pos_end=self.gstruc.length)
            if self.PHENOMAP_PLUS != []
            else Phenomap()
        )

        # Overshoot
        self.overshoot = Overshoot(
            OVERSHOOT_EVENT=self.OVERSHOOT_EVENT,
            MAX_POPULATION_SIZE=self.MAX_POPULATION_SIZE,
            CLIFF_SURVIVORSHIP=self.CLIFF_SURVIVORSHIP,
        )

        # Envmap
        self.envmap = (
            Envmap(
                BITS_PER_LOCUS=self.BITS_PER_LOCUS,
                total_loci=self.gstruc.length,
                ENVMAP_RATE=self.ENVMAP_RATE,
            )
            if self.ENVMAP_RATE > 0
            else Envmap()
        )

    def get_uids(self, n):
        """Get an array of unique origin identifiers"""
        uids = np.arange(n) + self.max_uid
        self.max_uid += n
        return uids
