import numpy as np


class Reproducer:
    def __init__(self, RECOMBINATION_RATE, MUTATION_RATIO):
        self.RECOMBINATION_RATE = RECOMBINATION_RATE
        self.MUTATION_RATIO = MUTATION_RATIO

    def recombine(self, genomes):
        """Return recombined genomes"""

        if self.RECOMBINATION_RATE == 0:
            return genomes

        # Recombine genomes
        flat_genomes = genomes.reshape(len(genomes), -1)
        chromosomes1 = flat_genomes[:, ::2]
        chromosomes2 = flat_genomes[:, 1::2]

        # Make choice array: when to take recombined and when to take original loci
        # -1 means synapse; +1 means clear
        rr = (
            self.RECOMBINATION_RATE / 2
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

    def assort(self, genomes):
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

    def mutate(self, genomes, muta_prob):
        
        random_probabilities = np.random.random(genomes.shape)

        # Broadcast to fit [individual, locus, bit] shape
        mutation_probabilities = muta_prob[:, None, None]

        mutate_0to1 = (genomes == 0) & (
            random_probabilities < (mutation_probabilities * self.MUTATION_RATIO)
        )
        mutate_1to0 = (genomes == 1) & (
            random_probabilities < mutation_probabilities
        )

        mutate = mutate_0to1 + mutate_1to0

        return np.logical_xor(genomes, mutate)