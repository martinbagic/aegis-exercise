from statistics import harmonic_mean
import numpy as np


def get_N(pop_size_history):
    return pop_size_history[-1]


def get_Ne(pop_size_history):
    return harmonic_mean(pop_size_history)


def allele_frequencies(genomes):
    return genomes.reshape(genomes.shape[0], -1).mean(0)


def genotype_frequencies(genomes, REPR_MODE):
    """Output: [loc1_bit1_freq00, loc1_bit1_freq01, loc1_bit1_freq11, loc1_bit2_freq00, ...]"""
    # TODO: Fetch REPR_MODE from params/panconfiguration
    if REPR_MODE != "asexual":
        len_pop = genomes.shape[0]

        genotypes_raw = genomes.reshape(-1, 2).sum(1).reshape(len_pop, -1).transpose()
        genotype_freqs = np.array([np.bincount(x, minlength=3) for x in genotypes_raw]).reshape(-1) / len_pop

        return genotype_freqs

    return allele_frequencies(genomes)


# class PopgenStats:
#     def __init__(self):
#         pass

#     def analyze(self, population):
#         """Calculate and return population genetic statistics"""

#         def pop_size():
#             return population.pop_size_history[-1]

#         def pop_size_effective():
#             return harmonic_mean(population.pop_size_history)

#         return (pop_size(), pop_size_effective())
