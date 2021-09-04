from statistics import harmonic_mean
from random import sample
from itertools import combinations
from math import sqrt
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
        genotype_freqs = (
            np.array([np.bincount(x, minlength=3) for x in genotypes_raw]).reshape(-1)
            / len_pop
        )

        return genotype_freqs

    return allele_frequencies(genomes)


def mean_H_per_bit(genomes, REPR_MODE):
    """Output: [Hloc1_bit1, Hloc1_bit2, ...] Entries: (bits_per_locus // 2) * nloci"""
    if REPR_MODE != "asexual":
        return genotype_frequencies(genomes, REPR_MODE)[1::3]

    return np.array([])


def mean_H_per_locus(genomes, REPR_MODE):
    """Output: [Hloc1, Hloc2, ...] Entries: nloci"""
    if REPR_MODE != "asexual":
        H = mean_H_per_bit(genomes, REPR_MODE)
        return H.reshape(-1, genomes.shape[2] >> 1).mean(1)

    return np.array([])


def mean_H(genomes, REPR_MODE):
    """Output: H"""
    if REPR_MODE != "asexual":
        return mean_H_per_bit(genomes, REPR_MODE).mean()

    return np.array([])


def mean_H_per_bit_expected(genomes, REPR_MODE):
    """Output: [Heloc1_bit1, Heloc1_bit2, ...] Entries: (bits_per_locus // 2) * nloci"""
    if REPR_MODE != "asexual":
        genotype_freqs_sqrd = genotype_frequencies(genomes, REPR_MODE) ** 2
        sum_each_locus = genotype_freqs_sqrd.reshape(-1, 3).sum(1)
        return 1 - sum_each_locus

    return np.array([])


def mean_H_expected(genomes, REPR_MODE):
    """Output: He"""
    if REPR_MODE != "asexual":
        return mean_H_per_bit_expected(genomes, REPR_MODE).mean()

    return np.array([])


def get_mu(G_muta_initial, G_muta_evolvable, gstruc, phenotypes):
    """Return equivalent of mutation rate µ per gene per generation -> AEGIS-'Locus' interpreted as a gene"""
    if G_muta_evolvable:
        return np.mean(phenotypes[:, gstruc["muta"].start])

    return G_muta_initial


def get_theta(REPR_MODE, Ne, mu):
    """Returns the adjusted mutation rate theta = 4 * Ne * µ"""
    ploidy_factor = 4 if REPR_MODE != "asexual" else 2
    theta = ploidy_factor * Ne * mu
    return theta


def reference_genome(genomes):
    """Returns the reference genome based on which allele is most common at each position. Equal fractions -> 0"""
    return np.round(genomes.reshape(genomes.shape[0], -1).mean(0)).astype("int32")


def segregating_sites(genomes, REPR_MODE="asexual"):
    """Returns the number of segregating sites"""
    if REPR_MODE == "asexual":
        pre_s = genomes.reshape(genomes.shape[0], -1).sum(0)
        s = genomes.shape[1] * genomes.shape[2] - (
            (pre_s == genomes.shape[0]).sum() + (pre_s == 0).sum()
        )
        return s

    pre_s = genomes.reshape(-1, 2).transpose().reshape(genomes.shape[0] << 1, -1).sum(0)
    s = ((genomes.shape[1] * genomes.shape[2]) >> 1) - (
        (pre_s == genomes.shape[0] << 1).sum() + (pre_s == 0).sum()
    )
    return s


def theta_w(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns Watterson's estimator theta_w"""
    if sample_size is None:
        sample_size = genomes.shape[0]

    def harmonic(x):
        return np.sum([1 / i for i in np.arange(1, x + 1)])

    if sample_provided and genomes.shape[0] > 1:
        s = segregating_sites(genomes, REPR_MODE)
        n = genomes.shape[0] if REPR_MODE == "asexual" else genomes.shape[0] << 1
        return s / harmonic(n - 1)

    if genomes.shape[0] > 1 and sample_size > 1:
        indices = sample(range(genomes.shape[0]), sample_size)
        genomes_sample = genomes[indices, :, :]
        s = segregating_sites(genomes_sample, REPR_MODE)
        n = sample_size if REPR_MODE == "asexual" else sample_size << 1
        return s / harmonic(n - 1)

    return np.array([])


def theta_pi(genomes, sample_size=None, sample_provided=True):
    """Returns the estimator theta_pi (based on pairwise differences)"""
    if sample_size == None:
        sample_size = genomes.shape[0]

    if sample_provided and genomes.shape[0] > 1:
        factor1 = 2 / (genomes.shape[0] * (genomes.shape[0] - 1))
        tmp = genomes.reshape(genomes.shape[0], -1)
        factor2 = np.array(
            [
                (tmp[i[0]] != tmp[i[1]]).sum()
                for i in combinations(range(genomes.shape[0]), 2)
            ]
        ).sum()
        return (factor1 * factor2) / genomes.shape[0]

    if genomes.shape[0] > 1 and sample_size > 1:
        factor1 = 2 / (sample_size * (sample_size - 1))
        indices = sample(range(genomes.shape[0]), sample_size)
        tmp = genomes.reshape(genomes.shape[0], -1)
        factor2 = np.array(
            [(tmp[i[0]] != tmp[i[1]]).sum() for i in combinations(indices, 2)]
        ).sum()
        return (factor1 * factor2) / sample_size

    return np.array([])


def tajimas_d(genomes, sample_size):
    """Returns Tajima's D"""
    indices = sample(range(genomes.shape[0]), sample_size)
    genomes_sample = genomes[indices, :, :]

    d = theta_pi(genomes_sample, sample_provided=True) - theta_w(
        genomes_sample, sample_provided=True
    )
    s = segregating_sites(genomes_sample)

    def harmonic(n):
        return np.sum([1 / i for i in np.arange(1, n + 1)])

    def harmonic_sq(n):
        return np.sum([1 / (i ** 2) for i in np.arange(1, n + 1)])

    a1 = harmonic(sample_size - 1)
    a2 = harmonic_sq(sample_size - 1)
    b1 = (sample_size + 1) / (3 * (sample_size - 1))
    b2 = (2 * (sample_size ** 2 + sample_size + 3)) / (
        9 * sample_size * (sample_size - 1)
    )
    c1 = b1 - (1 / a1)
    c2 = b2 - ((sample_size + 2) / a1 * sample_size) + (a2 / (a1 ** 2))
    e1 = c1 / a1
    e2 = c2 / ((a1 ** 2) + a2)
    dvar = sqrt((e1 * s) + (e2 * s * (s - 1)))

    return d / dvar


# class PopgenStats:
#     def __init__(self):
#         return
#
#     def test(self, gstruc, population):
#         return (
#             np.mean(population.phenotypes[:, gstruc["muta"].start]),
#             statistics.geometric_mean(population.phenotypes[:, gstruc["muta"].start]),
#             np.median(population.phenotypes[:, gstruc["muta"].start])
#         )
#

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
