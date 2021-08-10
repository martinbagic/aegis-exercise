import numpy as np

from aegis._deme.pop import Pop
from aegis import PAN

# TODO: fix reloading demes
# TODO: explicit sending of local parameters


class Deme:
    """Class that encodes the core, immutable aspects of the simulation"""

    def __init__(self, pop=None, popid=None, config=None, recorder=None):

        self.config = config
        self.popid = popid
        self.recorder = recorder
        self.eggs = None  # for split generations

        def _initialize_genomes():
            # Make a genome array with random values
            genomes = np.random.random(
                size=(
                    self.config.MAX_POPULATION_SIZE,
                    self.config.gstruc.length,
                    self.config.BITS_PER_LOCUS,
                )
            )

            # Make a bool map using the initial values from Traits
            for trait in self.config.gstruc.evolvable:
                genomes[:, trait.slice] = genomes[:, trait.slice] <= trait.initial

            genomes = genomes.astype(bool)

            # Guarantee survival and reproduction values up to first few mature ages
            if self.config.HEADSUP > -1:
                headsup = self.config.MATURATION_AGE + self.config.HEADSUP
                surv_start = self.config.gstruc["surv"].start
                repr_start = self.config.gstruc["repr"].start
                genomes[:, surv_start : surv_start + headsup] = True
                genomes[:, repr_start : repr_start + headsup] = True

            return genomes

        def _get_pop():
            if pop is None:
                num = self.config.MAX_POPULATION_SIZE

                genomes = _initialize_genomes()
                ages = np.zeros(num, int)
                origins = np.zeros(num, int) - 1
                uids = self.config.get_uids(num)
                births = np.zeros(num, int)
                birthdays = np.zeros(num, int)
                phenotypes = self._get_phenotype(genomes)
                return Pop(
                    genomes, ages, origins, uids, births, birthdays, phenotypes
                )
            else:
                return pop

        self.pop = _get_pop()

    #############
    # ONE CYCLE #
    #############

    def cycle(self):
        """Perform one simulation cycle"""

        if len(self.pop) + (0 if self.eggs is None else len(self.eggs)) == 0:
            return

        def _hatch_eggs(self):
            if self.eggs is not None:
                self.pop += self.eggs
                self.eggs = None

        self.recorder.record_snapshots(self.pop)
        self.recorder.record_visor(self.pop)

        if len(self.pop):
            self.eco_survival()
            self.gen_survival()
            self.reproduction()
            self.age()

        self.recorder.collect("cumulative_ages", self.pop.ages)

        self.config.season.countdown -= 1
        if self.config.season.countdown == 0:
            # Kill all living, hatch eggs, and restart season
            mask_kill = np.ones(len(self.pop), bool)
            self._kill(mask_kill, "season_shift")
            _hatch_eggs(self)
            self.config.season.reset()

        elif self.config.season.countdown == float("inf"):
            # Add newborns to population
            _hatch_eggs(self)

        # Evolve envmap if applicable
        self.config.envmap.evolve(stage=PAN.stage)

        # Pickle self
        self.recorder.record_pickle(self)

    def terminate(self):
        # Pickle the current population
        self.recorder.record_pickle(self)

        # Kill the current population
        mask_kill = np.ones(len(self.pop), bool)
        self._kill(mask_kill, "end_of_sim")

    ###############
    # CYCLE LOGIC #
    ###############

    def age(self):
        """Increase age of all by one and kill those that surpass max lifespan"""
        self.pop.ages += 1
        mask_kill = self.pop.ages >= self.config.MAX_LIFESPAN
        self._kill(mask_kill=mask_kill, causeofdeath="max_lifespan")

    def eco_survival(self):
        """Impose ecological death, i.e. death that arises due to resource scarcity"""
        mask_kill = self.config.overshoot(n=len(self.pop))
        self._kill(mask_kill=mask_kill, causeofdeath="overshoot")

    def gen_survival(self):
        """Impose genomic death, i.e. death that arises with probability encoded in the genome"""
        probs_surv = self._get_evaluation("surv")
        mask_surv = np.random.random(len(probs_surv)) < probs_surv
        self._kill(mask_kill=~mask_surv, causeofdeath="genetic")

    def reproduction(self):
        """Let individuals reproduce"""

        def _recombine(genomes):
            """Return recombined genomes"""

            if self.config.RECOMBINATION_RATE == 0:
                return genomes

            # Recombine genomes
            flat_genomes = genomes.reshape(len(genomes), -1)
            chromosomes1 = flat_genomes[:, ::2]
            chromosomes2 = flat_genomes[:, 1::2]

            # Make choice array: when to take recombined and when to take original loci
            # -1 means synapse; +1 means clear
            rr = (
                self.config.RECOMBINATION_RATE / 2
            )  # / 2 because you are generating two random vectors (fwd and bkd)
            reco_fwd = (np.random.random(chromosomes1.shape) < rr) * -2 + 1
            reco_bkd = (np.random.random(chromosomes2.shape) < rr) * -2 + 1

            # Propagate synapse
            reco_fwd_cum = np.cumprod(reco_fwd, axis=1)
            reco_bkd_cum = np.cumprod(reco_bkd[:, ::-1], axis=1)[:, ::-1]

            # Recombine if both sites recombining
            reco_final = (reco_fwd_cum + reco_bkd_cum) == -2

            # Choose bits from first or second chromosome
            recombined = np.empty(flat_genomes.shape, bool)
            recombined[:, ::2] = np.choose(reco_final, [chromosomes1, chromosomes2])
            recombined[:, 1::2] = np.choose(reco_final, [chromosomes2, chromosomes1])
            recombined = recombined.reshape(genomes.shape)

            # Check one example that bits are recombining
            if reco_final[0, 0]:
                assert (
                    recombined[0, 0, 0] == chromosomes2[0, 0]
                    and recombined[0, 0, 1] == chromosomes1[0, 0]
                )
            else:
                assert (
                    recombined[0, 0, 0] == chromosomes1[0, 0]
                    and recombined[0, 0, 1] == chromosomes2[0, 0]
                )

            return recombined

        def _assort(genomes):
            """Return assorted chromosomes"""
            # Locus structure of an example with 8 bits:
            # [1 2 1 2 1 2 1 2]
            # [x   x   x   x  ] => 1st chromosome
            # [  x   x   x   x] => 2nd chromosome

            # Extract parent indices twice, and shuffle
            order = np.repeat(np.arange(len(genomes)), 2)
            np.random.shuffle(order)

            # Check for selfing (selfing when pair contains equal parent indices)
            selfed = (order[::2] == order[1::2]).nonzero()[0] * 2

            if len(selfed) == 1:
                # If one parent index pair is selfed, swap first selfed chromosome with the first chromosome of the previous or next pair
                offset = -2 if selfed[0] > 0 else 2
                order[selfed], order[selfed + offset] = (
                    order[selfed + offset],
                    order[selfed],
                )
            elif len(selfed) > 1:
                # If multiple parent index pairs are selfed, shift first chromosomes of selfed pairs
                order[selfed] = order[np.roll(selfed, 1)]

            assorted = genomes[order]

            # Children chromosomes are at positions [::2]
            # Copy second chromosome of second parent onto the second chromosome of the children
            # Thus, children have the first chromosomes from the first parents and the second chromosomes from the second parents
            assorted[::2, :, 1::2] = assorted[1::2, :, 1::2]
            assorted = assorted[::2]

            return assorted, order

        def _mutate(genomes):
            """Return mutated genomes"""
            muta_prob = self._get_evaluation("muta", part=mask_repr)
            muta_prob = muta_prob[mask_repr]

            random_probabilities = np.random.random(genomes.shape)

            # Broadcast to fit [individual, locus, bit] shape
            mutation_probabilities = muta_prob[:, None, None]

            mutate_0to1 = (genomes == 0) & (
                random_probabilities
                < (mutation_probabilities * self.config.MUTATION_RATIO)
            )
            mutate_1to0 = (genomes == 1) & (
                random_probabilities < mutation_probabilities
            )

            mutate = mutate_0to1 + mutate_1to0

            return np.logical_xor(genomes, mutate)

        # Check if mature
        mask_mature = self.pop.ages >= self.config.MATURATION_AGE
        if not any(mask_mature):
            return

        # Check if reproducing
        probs_repr = self._get_evaluation("repr", part=mask_mature)
        mask_repr = np.random.random(len(probs_repr)) < probs_repr
        if sum(mask_repr) < 2:  # Forgo if not at least two available parents
            return

        # Count ages at reproduction
        ages_repr = self.pop.ages[mask_repr]
        # self.macroconfig.counter.count("age_at_birth", ages_repr)
        self.recorder.collect("age_at_birth", ages_repr)

        # Increase births statistics
        self.pop.births += mask_repr

        # Copy genomes of parents and modify
        genomes = self.pop.genomes[mask_repr]
        if self.config.REPR_MODE == "sexual":
            genomes = _recombine(genomes)
            genomes, order = _assort(genomes)
        genomes = _mutate(genomes)

        # Get origins
        if self.config.REPR_MODE in ("asexual", "diasexual"):
            origins = self.pop.uids[mask_repr]
        elif self.config.REPR_MODE == "sexual":
            origins = np.array(
                [
                    f"{self.pop.uids[order[2*i]]}.{self.pop.uids[order[2*i+1]]}"
                    for i in range(len(order) // 2)
                ]
            )

        # Get eggs
        n = len(genomes)
        eggs = Pop(
            genomes=genomes,
            ages=np.zeros(n, int),
            origins=origins,
            uids=self.config.get_uids(n),
            births=np.zeros(n, int),
            birthdays=np.zeros(n, int) + PAN.stage,
            phenotypes=self._get_phenotype(genomes),
        )

        if self.eggs is None:
            self.eggs = eggs
        else:
            self.eggs += eggs

    ################
    # HELPER FUNCS #
    ################

    def _get_phenotype(self, genomes):
        def _get_interpretome(omes):
            """Interpret genomes"""
            interpretome = np.zeros(shape=omes.shape[:2])

            for trait in self.config.gstruc.evolvable:
                # fetch
                loci = omes[:, trait.slice]

                # interpret
                probs = self.config.interpreter(loci, trait.interpreter)

                # add back
                interpretome[:, trait.slice] += probs

            return interpretome

        def _bound(omes):
            """Impose lower and upper bounds for genetically encodable attributes."""
            for trait in self.config.gstruc.evolvable:
                lo, hi = trait.lo, trait.hi
                omes[:, trait.slice] = omes[:, trait.slice] * (hi - lo) + lo
            return omes

        envgenomes = self.config.envmap(genomes)
        interpretome = _get_interpretome(envgenomes)
        phenotypes = self.config.phenomap(interpretome)
        bounded_phenotypes = _bound(phenotypes)

        return bounded_phenotypes

    def _get_evaluation(self, attr, part=None):

        which_individuals = np.arange(len(self.pop))
        if part is not None:
            which_individuals = which_individuals[part]

        # first scenario
        trait = self.config.gstruc[attr]
        if not trait.evolvable:
            probs = trait.initial

        # second and third scenario
        if trait.evolvable:
            which_loci = trait.start
            if trait.agespec:
                which_loci += self.pop.ages[which_individuals]

            probs = self.pop.phenotypes[which_individuals, which_loci]

        # expand values back into an array with shape of whole pop
        final_probs = np.zeros(len(self.pop))
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
            ages_death = self.pop.ages[mask_kill]
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
        # self.recorder.rec(self.pop[mask_record], causeofdeath, self.popid)

        # Retain survivors
        self.pop *= ~mask_kill

    def __len__(self):
        """Return the number of living individuals and saved eggs"""
        return (
            len(self.pop) + len(self.eggs) if self.eggs is not None else len(self.pop)
        )
