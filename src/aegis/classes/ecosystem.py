import numpy as np

from aegis.classes.interpreter import Interpreter
from aegis.classes.reproducer import Reproducer
from aegis.classes.overshoot import Overshoot
from aegis.classes.pleiotropy import Pleiotropy
from aegis.classes.recorder import Recorder
from aegis.classes.season import Season
from aegis.classes.environment import Environment
from aegis.classes.gstruc import Gstruc
from aegis.classes.population import Population

from aegis.panconfiguration import pan


class Ecosystem:
    """Container for one ecosystem"""

    ecosystem_id = 1

    def __init__(self, params, population=None):

        self.ecosystem_id = Ecosystem.ecosystem_id
        Ecosystem.ecosystem_id += 1

        # Save ecosystem parameters
        self.MAX_LIFESPAN = params["MAX_LIFESPAN"]  # used in self.age()
        self.MATURATION_AGE = params["MATURATION_AGE"]  # used in self.reproduction()
        self.REPR_MODE = params["REPR_MODE"]  # used in self.reproduction()

        # Initialize ecosystem variables
        self.max_uid = 0  # ID of the most recently born individual

        # Initialize recorder
        self.recorder = Recorder(
            ecosystem_id=self.ecosystem_id,
            MAX_LIFESPAN=params["MAX_LIFESPAN"],
        )
        self.recorder.record_input_summary(params)  # Record input summary

        # Initialize genome structure
        self.gstruc = Gstruc(params)  # TODO you cannot pass params

        # Initialize reproducer
        self.reproducer = Reproducer(
            RECOMBINATION_RATE=params["RECOMBINATION_RATE"],
            MUTATION_RATIO=params["MUTATION_RATIO"],
        )

        # Initialize season
        self.season = Season(DISCRETE_GENERATIONS=params["DISCRETE_GENERATIONS"])

        # Initialize interpreter
        self.interpreter = Interpreter(
            BITS_PER_LOCUS=params["BITS_PER_LOCUS"],
            REPR_MODE=params["REPR_MODE"],
        )

        # Initialize pleiotropy
        self.pleiotropy = (
            Pleiotropy(PLEIOTROPY_SPECS=params["PLEIOTROPY_SPECS"], pos_end=self.gstruc.length)
            if params["PLEIOTROPY_SPECS"] != []
            else Pleiotropy()
        )

        # Initialize overshoot
        self.overshoot = Overshoot(
            OVERSHOOT_EVENT=params["OVERSHOOT_EVENT"],
            MAX_POPULATION_SIZE=params["MAX_POPULATION_SIZE"],
            CLIFF_SURVIVORSHIP=params["CLIFF_SURVIVORSHIP"],
        )

        # Initialize environmental map
        self.environment = (
            Environment(
                BITS_PER_LOCUS=params["BITS_PER_LOCUS"],
                total_loci=self.gstruc.length,
                ENVIRONMENT_CHANGE_RATE=params["ENVIRONMENT_CHANGE_RATE"],
            )
            if params["ENVIRONMENT_CHANGE_RATE"] > 0
            else Environment()
        )

        # TODO transfer into population.py
        # Initialize population
        def _initialize_genomes():
            # Make a genome array with random values
            genomes = np.random.random(
                size=(
                    params["MAX_POPULATION_SIZE"],
                    self.gstruc.length,
                    params["BITS_PER_LOCUS"],
                )
            )

            # Make a bool map using the initial values from Traits
            for trait in self.gstruc.evolvable:
                genomes[:, trait.slice] = genomes[:, trait.slice] <= trait.initial

            genomes = genomes.astype(bool)

            # Guarantee survival and reproduction values up to first few mature ages
            if params["HEADSUP"] > -1:
                headsup = params["MATURATION_AGE"] + params["HEADSUP"]
                surv_start = self.gstruc["surv"].start
                repr_start = self.gstruc["repr"].start
                genomes[:, surv_start : surv_start + headsup] = True
                genomes[:, repr_start : repr_start + headsup] = True

            return genomes

        def _get_pop():
            if population is None:
                num = params["MAX_POPULATION_SIZE"]

                genomes = _initialize_genomes()
                ages = np.zeros(num, int)
                origins = np.zeros(num, int) - 1
                uids = self._get_n_uids(num)
                births = np.zeros(num, int)
                birthdays = np.zeros(num, int)
                phenotypes = self._get_phenotype(genomes)
                return Population(
                    genomes, ages, origins, uids, births, birthdays, phenotypes
                )
            else:
                return population

        self.population = _get_pop()
        self.eggs = None  # for discrete generations

    ##############
    # MAIN LOGIC #
    ##############

    def cycle(self):
        """Perform one simulation cycle"""

        # If extinct, do nothing
        if self.recorder.extinct:
            return

        def _hatch_eggs(self):
            if self.eggs is not None:
                self.population += self.eggs
                self.eggs = None

        self.recorder.record_snapshots(self.population)
        self.recorder.record_visor(self.population)

        if len(self.population):
            self.eco_survival()
            self.gen_survival()
            self.reproduction()
            self.age()

        self.recorder.collect("cumulative_ages", self.population.ages)

        self.season.countdown -= 1
        if self.season.countdown == 0:
            # Kill all living, hatch eggs, and restart season
            mask_kill = np.ones(len(self.population), bool)
            self._kill(mask_kill, "season_shift")
            _hatch_eggs(self)
            self.season.reset()

        elif self.season.countdown == float("inf"):
            # Add newborns to population
            _hatch_eggs(self)

        # Evolve environment if applicable
        self.environment.evolve(stage=pan.stage)

        # Pickle self
        self.recorder.record_pickle(self)

        if len(self) == 0:
            self.recorder.extinct = True

    # FOR REFERENCE
    # def terminate(self):
    #     # Pickle the current population
    #     self.recorder.record_pickle(self)

    #     # Kill the current population
    #     mask_kill = np.ones(len(self.population), bool)
    #     self._kill(mask_kill, "end_of_sim")

    ###############
    # CYCLE LOGIC #
    ###############

    def age(self):
        """Increase age of all by one and kill those that surpass max lifespan"""
        self.population.ages += 1
        mask_kill = self.population.ages >= self.MAX_LIFESPAN
        self._kill(mask_kill=mask_kill, causeofdeath="max_lifespan")

    def eco_survival(self):
        """Impose ecological death, i.e. death that arises due to resource scarcity"""
        mask_kill = self.overshoot(n=len(self.population))
        self._kill(mask_kill=mask_kill, causeofdeath="overshoot")

    def gen_survival(self):
        """Impose genomic death, i.e. death that arises with probability encoded in the genome"""
        probs_surv = self._get_evaluation("surv")
        mask_surv = np.random.random(len(probs_surv)) < probs_surv
        self._kill(mask_kill=~mask_surv, causeofdeath="genetic")

    def reproduction(self):
        """Let individuals reproduce"""

        # Check if mature
        mask_mature = self.population.ages >= self.MATURATION_AGE
        if not any(mask_mature):
            return

        # Check if reproducing
        probs_repr = self._get_evaluation("repr", part=mask_mature)
        mask_repr = np.random.random(len(probs_repr)) < probs_repr
        if sum(mask_repr) < 2:  # Forgo if not at least two available parents
            return

        # Count ages at reproduction
        ages_repr = self.population.ages[mask_repr]
        self.recorder.collect("age_at_birth", ages_repr)

        # Increase births statistics
        self.population.births += mask_repr

        # Copy genomes of parents and modify
        genomes = self.population.genomes[mask_repr]
        if self.REPR_MODE == "sexual":
            genomes = self.reproducer.recombine(genomes)
            genomes, order = self.reproducer.assort(genomes)

        muta_prob = self._get_evaluation("muta", part=mask_repr)
        muta_prob = muta_prob[mask_repr]
        genomes = self.reproducer.mutate(genomes, muta_prob)

        # Get origins
        if self.REPR_MODE in ("asexual", "asexual_diploid"):
            origins = self.population.uids[mask_repr]
        elif self.REPR_MODE == "sexual":
            origins = np.array(
                [
                    f"{self.population.uids[order[2*i]]}.{self.population.uids[order[2*i+1]]}"
                    for i in range(len(order) // 2)
                ]
            )

        # Get eggs
        n = len(genomes)
        eggs = Population(
            genomes=genomes,
            ages=np.zeros(n, int),
            origins=origins,
            uids=self._get_n_uids(n),
            births=np.zeros(n, int),
            birthdays=np.zeros(n, int) + pan.stage,
            phenotypes=self._get_phenotype(genomes),
        )

        if self.eggs is None:
            self.eggs = eggs
        else:
            self.eggs += eggs

    ################
    # HELPER FUNCS #
    ################

    def _get_n_uids(self, n):
        """Get an array of unique origin identifiers"""
        uids = np.arange(n) + self.max_uid
        self.max_uid += n
        return uids

    def _get_phenotype(self, genomes):
        def _get_interpretome(omes):
            """Interpret genomes"""
            interpretome = np.zeros(shape=omes.shape[:2])

            for trait in self.gstruc.evolvable:
                # fetch
                loci = omes[:, trait.slice]

                # interpret
                probs = self.interpreter(loci, trait.interpreter)

                # add back
                interpretome[:, trait.slice] += probs

            return interpretome

        def _bound(omes):
            """Impose lower and upper bounds for genetically encodable attributes."""
            for trait in self.gstruc.evolvable:
                lo, hi = trait.lo, trait.hi
                omes[:, trait.slice] = omes[:, trait.slice] * (hi - lo) + lo
            return omes

        envgenomes = self.environment(genomes)
        interpretome = _get_interpretome(envgenomes)
        phenotypes = self.pleiotropy(interpretome)
        bounded_phenotypes = _bound(phenotypes)

        return bounded_phenotypes

    def _get_evaluation(self, attr, part=None):

        which_individuals = np.arange(len(self.population))
        if part is not None:
            which_individuals = which_individuals[part]

        # first scenario
        trait = self.gstruc[attr]
        if not trait.evolvable:
            probs = trait.initial

        # second and third scenario
        if trait.evolvable:
            which_loci = trait.start
            if trait.agespec:
                which_loci += self.population.ages[which_individuals]

            probs = self.population.phenotypes[which_individuals, which_loci]

        # expand values back into an array with shape of whole population
        final_probs = np.zeros(len(self.population))
        final_probs[which_individuals] += probs

        return final_probs

    def _kill(self, mask_kill, causeofdeath):
        """
        Kill individuals and record their data.
        Killing can occur due to age, genomic death, ecological death, and season shift.
        """

        # Skip if no one to kill
        if not any(mask_kill):
            return

        # Count ages at death
        if causeofdeath != "max_lifespan":
            ages_death = self.population.ages[mask_kill]
            # self.macroconfig.counter.count(f"age_at_{causeofdeath}", ages_death)
            self.recorder.collect(f"age_at_{causeofdeath}", ages_death)

        ### KEEP THIS FOR REFERENCE ###
        #
        # Record (some or all) of killed individuals
        # mask_record = (
        #     mask_kill.nonzero()[0][:: self.macroconfig.REC_EVERY_NTH]
        #     if self.macroconfig.REC_EVERY_NTH > 1
        #     else mask_kill
        # )
        # self.recorder.rec(self.population[mask_record], causeofdeath, self.ecosystem_id)

        # Retain survivors
        self.population *= ~mask_kill

    def __len__(self):
        """Return the number of living individuals and saved eggs"""
        return (
            len(self.population) + len(self.eggs)
            if self.eggs is not None
            else len(self.population)
        )
