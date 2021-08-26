from statistics import harmonic_mean
import numpy as np


class PopgenStats:
    def __init__(self):
        pass

    def analyze(self, population):
        """Calculate and return population genetic statistics"""

        def pop_size():
            return population.pop_size_history[-1]

        def pop_size_effective():
            return harmonic_mean(population.pop_size_history)

        def allele_frequencies():
            return population.genomes.reshape(len(population), -1).mean(0)

        def genotype_frequencies():
            """Output: [loc1_bit1_freq00, loc1_bit1_freq01, loc1_bit1_freq11, loc1_bit2_freq00, ...]"""
            # TODO: Run this only if REPR_MODE != "asexual"
            # TODO: Fetch REPR_MODE, MAX_LIFESPAN and BITS_PER_LOCUS from params/panconfiguration
            MAX_LIFESPAN = 50
            BITS_PER_LOCUS = 8

            len_pop = len(population)
            genotypes_raw = (
                population.genomes.reshape(-1, 2)
                .sum(1)
                .reshape(len_pop, (MAX_LIFESPAN * 2), (BITS_PER_LOCUS // 2))
            )
            genotype_freqs = np.zeros(shape=(MAX_LIFESPAN * 2, BITS_PER_LOCUS // 2, 3))

            for i in range(MAX_LIFESPAN * 2):
                for j in range(BITS_PER_LOCUS // 2):
                    tmp = np.bincount(genotypes_raw[:, i, j]) / len_pop
                    genotype_freqs[i, j, 0] = tmp[0]
                    genotype_freqs[i, j, 1] = tmp[1]
                    genotype_freqs[i, j, 2] = tmp[2]

            return genotype_freqs.reshape(-1)

        return ()
