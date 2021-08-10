import numpy as np
from class_logic.interpreter import Interpreter
from class_logic.phenomap import Phenomap
from class_logic.overshoot import Overshoot
from class_logic.envmap import Envmap
from class_logic.season import Season

from class_data.gstruc import Gstruc, Trait


class Config:
    """Wrapper for biosystem-specific parameters"""

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
        self.gstruc = Gstruc(
            traits=[Trait(name, params) for name in ["surv", "repr", "neut", "muta"]]
        )

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
            Phenomap(PHENOMAP_PLUS=self.PHENOMAP_PLUS, pos_end=Trait.genome_length)
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
                total_loci=Trait.genome_length,
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
