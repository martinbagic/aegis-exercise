import numpy as np

from aegis.panconfiguration import pan


class Reproducer:
    def __init__(self, RECOMBINATION_RATE, MUTATION_RATIO):
        self.RECOMBINATION_RATE = RECOMBINATION_RATE
        self.MUTATION_RATIO = MUTATION_RATIO

    def recombine(self, genomes):
        """Return recombined genomes"""

        if self.RECOMBINATION_RATE == 0:
            return genomes

        # TODO note that both recombined ("complementary") gametes are used

        # Recombine genomes

        # TODO be explicit with dimensions, coupling with gstruc
        flat_genomes = genomes.reshape(len(genomes), 2, -1)
        chromatid1 = flat_genomes[:, 0]
        chromatid2 = flat_genomes[:, 1]

        # Make choice array: when to take recombined and when to take original loci
        # -1 means synapse; +1 means clear
        rr = (
            self.RECOMBINATION_RATE / 2
        )  # / 2 because you are generating two random vectors (fwd and bkd)
        reco_fwd = (pan.rng.random(chromatid1.shape) < rr) * -2 + 1
        reco_bkd = (pan.rng.random(chromatid2.shape) < rr) * -2 + 1

        # Propagate synapse
        reco_fwd_cum = np.cumprod(reco_fwd, axis=1)
        reco_bkd_cum = np.cumprod(reco_bkd[:, ::-1], axis=1)[:, ::-1]

        # Recombine if both sites recombining
        reco_final = (reco_fwd_cum + reco_bkd_cum) == -2

        # Choose bits from first or second chromosome
        # recombined = np.empty(flat_genomes.shape, bool)
        recombined = np.empty(flat_genomes.shape, bool)
        recombined[:, 0] = np.choose(reco_final, [chromatid1, chromatid2])
        recombined[:, 1] = np.choose(reco_final, [chromatid2, chromatid1])
        recombined = recombined.reshape(genomes.shape)

        return recombined

    def assort(self, genomes):
        """Return assorted chromatids"""

        # Extract parent indices twice, and shuffle
        order = np.repeat(np.arange(len(genomes)), 2)
        pan.rng.shuffle(order)

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

        # Extract gametes
        gametes = genomes[order]

        # Unify gametes
        children = np.empty(genomes.shape, bool)
        children[:, 0] = gametes[::2, 0]  # 1st chromatid from 1st parent
        children[:, 1] = gametes[1::2, 1]  # 2nd chromatid from 2nd parent

        return children, order

    def mutate(self, genomes, muta_prob):

        random_probabilities = pan.rng.random(genomes.shape)

        # Broadcast to fit [individual, chromatid, locus, bit] shape
        mutation_probabilities = muta_prob[:, None, None, None]

        rate_0to1 = self.MUTATION_RATIO / (1 + self.MUTATION_RATIO)
        rate_1to0 = 1 / (1 + self.MUTATION_RATIO)

        mutate_0to1 = (genomes == 0) & (
            random_probabilities < (mutation_probabilities * rate_0to1)
        )
        mutate_1to0 = (genomes == 1) & (
            random_probabilities < (mutation_probabilities * rate_1to0)
        )

        mutate = mutate_0to1 + mutate_1to0

        return np.logical_xor(genomes, mutate)
