import numpy as np
from class_logic.interpreter import Interpreter
from class_logic.phenomap import Phenomap, PhenomapFake
from class_logic.overshoot import Overshoot
from class_logic.envmap import Envmap, EnvmapFake
from class_logic.season import Season


class Config:
    """Wrapper for all configuration parameters"""

    def __init__(self, params):

        # Population parameters
        self.MAX_LIFESPAN = params["MAX_LIFESPAN"]
        self.MATURATION_AGE = params["MATURATION_AGE"]
        self.BITS_PER_LOCUS = params["BITS_PER_LOCUS"]
        self.HEADSUP = params["HEADSUP"]
        self.GENOME_STRUCT = params["GENOME_STRUCT"]
        self.GENOME_CONST = params["GENOME_CONST"]
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

        # Derived parameters
        self.loci_n = {
            attr: [1, self.MAX_LIFESPAN][vals[0]]
            for attr, vals in self.GENOME_STRUCT.items()
        }  # Which loci correspond to which traits
        loci_pos = [0] + np.cumsum(list(self.loci_n.values())).tolist()
        self.loci_pos = {
            attr: (loci_pos[i], loci_pos[i + 1])
            for i, attr in enumerate(self.GENOME_STRUCT)
        }  # First and last+1 loci of each trait
        self.total_loci = loci_pos[-1]  # Total number of loci

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
            Phenomap(PHENOMAP_PLUS=self.PHENOMAP_PLUS, pos_end=self.total_loci)
            if self.PHENOMAP_PLUS != []
            else PhenomapFake()
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
                total_loci=self.total_loci,
                ENVMAP_RATE=self.ENVMAP_RATE,
            )
            if self.ENVMAP_RATE > 0
            else EnvmapFake()
        )

    def get_uids(self, n):
        """Get an array of unique origin identifiers"""
        uids = np.arange(n) + self.max_uid
        self.max_uid += n
        return uids
