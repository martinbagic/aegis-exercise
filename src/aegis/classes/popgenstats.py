import statistics
import itertools
import numpy as np


def get_N(pop_size_history):
    return pop_size_history[-1]


def get_Ne(pop_size_history):
    return statistics.harmonic_mean(pop_size_history)


def allele_frequencies(genomes):
    return genomes.reshape(genomes.shape[0], -1).mean(0)


def genotype_frequencies(genomes, REPR_MODE):
    """Output: [loc1_bit1_freq00, loc1_bit1_freq01, loc1_bit1_freq11, loc1_bit2_freq00, ...]"""
    if REPR_MODE == "asexual":
        return allele_frequencies(genomes)

    # TODO: Fetch REPR_MODE from params/panconfiguration
    len_pop = genomes.shape[0]

    genotypes_raw = genomes.reshape(-1, 2).sum(1).reshape(len_pop, -1).transpose()
    genotype_freqs = (
        np.array([np.bincount(x, minlength=3) for x in genotypes_raw]).reshape(-1)
        / len_pop
    )

    return genotype_freqs


def mean_H_per_bit(genomes, REPR_MODE):
    """Output: [Hloc1_bit1, Hloc1_bit2, ...] Entries: (bits_per_locus // 2) * nloci"""
    if REPR_MODE == "asexual":
        return np.array([])

    return genotype_frequencies(genomes, REPR_MODE)[1::3]


def mean_H_per_locus(genomes, REPR_MODE):
    """Output: [Hloc1, Hloc2, ...] Entries: nloci"""
    if REPR_MODE == "asexual":
        return np.array([])

    H = mean_H_per_bit(genomes, REPR_MODE)
    return H.reshape(-1, genomes.shape[2] >> 1).mean(1)


def mean_H(genomes, REPR_MODE):
    """Output: H"""
    if REPR_MODE == "asexual":
        return np.array([])

    return mean_H_per_bit(genomes, REPR_MODE).mean()


def mean_H_per_bit_expected(genomes, REPR_MODE):
    """Output: [Heloc1_bit1, Heloc1_bit2, ...] Entries: (bits_per_locus // 2) * nloci"""
    if REPR_MODE == "asexual":
        return np.array([])

    genotype_freqs_sqrd = genotype_frequencies(genomes, REPR_MODE) ** 2
    sum_each_locus = genotype_freqs_sqrd.reshape(-1, 3).sum(1)
    return 1 - sum_each_locus


def mean_H_expected(genomes, REPR_MODE):
    """Output: He"""
    if REPR_MODE == "asexual":
        return np.array([])

    return mean_H_per_bit_expected(genomes, REPR_MODE).mean()


def get_mu(G_muta_initial, G_muta_evolvable, gstruc, phenotypes):
    """Return equivalent of mutation rate µ per gene per generation -> AEGIS-'Locus' interpreted as a gene"""
    if not G_muta_evolvable:
        return G_muta_initial

    return np.mean(phenotypes[:, gstruc["muta"].start])


def get_theta(REPR_MODE, Ne, mu):
    """Returns the adjusted mutation rate theta = 4 * Ne * µ"""
    ploidy_factor = 2 if REPR_MODE == "asexual" else 4
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


def harmonic(x):
    return np.sum([1 / i for i in np.arange(1, x + 1)])


def harmonic_sq(n):
    return np.sum([1 / (i ** 2) for i in np.arange(1, n + 1)])


def theta_w(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns Watterson's estimator theta_w"""
    if REPR_MODE != "asexual":
        genomes = (
            genomes.reshape(-1, 2)
            .transpose()
            .reshape(genomes.shape[0] << 1, genomes.shape[1], -1)
        )

    if sample_size is None:
        sample_size = genomes.shape[0]

    if sample_size < 2 or genomes.shape[0] < 2:
        return np.array([])

    if sample_provided:
        genomes_sample = genomes

    else:
        indices = np.random.choice(range(genomes.shape[0]), sample_size, replace=False)
        genomes_sample = genomes[indices, :, :]

    s = segregating_sites(genomes_sample)
    return s / harmonic(sample_size - 1)


def theta_pi(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns the estimator theta_pi (based on pairwise differences)"""
    if REPR_MODE != "asexual":
        genomes = (
            genomes.reshape(-1, 2)
            .transpose()
            .reshape(genomes.shape[0] << 1, genomes.shape[1], -1)
        )

    if sample_size is None:
        sample_size = genomes.shape[0]

    if sample_size < 2 or genomes.shape[0] < 2:
        return np.array([])

    if sample_provided:
        genomes_sample = genomes

    else:
        indices = np.random.choice(range(genomes.shape[0]), sample_size, replace=False)
        genomes_sample = genomes[indices, :, :]

    combs = itertools.combinations(range(sample_size), 2)
    tmp = genomes_sample.reshape(sample_size, -1)
    diffs = np.array([(tmp[i[0]] != tmp[i[1]]).sum() for i in combs])
    total_diffs = diffs.sum()
    ncomparisons = diffs.size

    return total_diffs / ncomparisons


def tajimas_d(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns Tajima's D"""
    if REPR_MODE != "asexual":
        genomes = (
            genomes.reshape(-1, 2)
            .transpose()
            .reshape(genomes.shape[0] << 1, genomes.shape[1], -1)
        )

    if sample_size is None:
        sample_size = genomes.shape[0]

    if sample_size < 3 or genomes.shape[0] < 3:
        return np.array([])

    if sample_provided:
        genomes_sample = genomes

    else:
        indices = np.random.choice(range(genomes.shape[0]), sample_size, replace=False)
        genomes_sample = genomes[indices, :, :]

    d = theta_pi(genomes_sample) - theta_w(genomes_sample)
    s = segregating_sites(genomes_sample)

    a1 = harmonic(sample_size - 1)
    a2 = harmonic_sq(sample_size - 1)
    b1 = (sample_size + 1) / (3 * (sample_size - 1))
    b2 = (2 * (sample_size ** 2 + sample_size + 3)) / (
        9 * sample_size * (sample_size - 1)
    )
    c1 = b1 - (1 / a1)
    c2 = b2 - ((sample_size + 2) / (a1 * sample_size)) + (a2 / (a1 ** 2))
    e1 = c1 / a1
    e2 = c2 / ((a1 ** 2) + a2)
    dvar = ((e1 * s) + (e2 * s * (s - 1))) ** 0.5

    return d / dvar


def theta_h(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns Fay and Wu's estimator theta_h"""
    if REPR_MODE != "asexual":
        genomes = (
            genomes.reshape(-1, 2)
            .transpose()
            .reshape(genomes.shape[0] << 1, genomes.shape[1], -1)
        )

    if sample_size is None:
        sample_size = genomes.shape[0]

    if sample_size < 2 or genomes.shape[0] < 2:
        return np.array([])

    if sample_provided:
        genomes_sample = genomes

    else:
        indices = np.random.choice(range(genomes.shape[0]), sample_size, replace=False)
        genomes_sample = genomes[indices, :, :]

    # sum from i=1 to i=n-1: ( (2 * S_i * i^2) / (n * (n-1)) )
    ref = reference_genome(genomes)
    pre_s = genomes_sample.reshape(genomes_sample.shape[0], -1).sum(0)
    pre_s[np.nonzero(ref)] -= sample_size
    pre_s = np.abs(pre_s)
    s = np.bincount(pre_s, minlength=sample_size + 1)[:-1]
    t_h = (
        (2 * s * (np.arange(sample_size) ** 2)) / (sample_size * (sample_size - 1))
    ).sum()
    return t_h


def fayandwu_h(genomes, sample_size=None, REPR_MODE="asexual", sample_provided=False):
    """Returns Fay and Wu's H"""
    if REPR_MODE != "asexual":
        genomes = (
            genomes.reshape(-1, 2)
            .transpose()
            .reshape(genomes.shape[0] << 1, genomes.shape[1], -1)
        )

    if sample_size is None:
        sample_size = genomes.shape[0]

    if sample_size < 2 or genomes.shape[0] < 2:
        return np.array([])

    if sample_provided:
        genomes_sample = genomes

    else:
        indices = np.random.choice(range(genomes.shape[0]), sample_size, replace=False)
        genomes_sample = genomes[indices, :, :]

    h = theta_pi(genomes_sample) - theta_h(genomes_sample)
    hvar = 1  # TODO: Calculate actual variance of h
    return h / hvar


# class PopgenStats:
#     def __init__(self):
#         return
#
#     def analyze(self, population):
#         return population.genomes.reshape(-1)


#

# class PopgenStats:
#     def __init__(self):
#         pass

#     def analyze(self, population):
#         """Calculate and return population genetic statistics"""

#         def pop_size():
#             return population.pop_size_history[-1]

#         def pop_size_effective():
#             return statistics.harmonic_mean(population.pop_size_history)

#         return (pop_size(), pop_size_effective())
