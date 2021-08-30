from statistics import harmonic_mean


def get_N(pop_size_history):
    return pop_size_history[-1]


def get_Ne(pop_size_history):
    return harmonic_mean(pop_size_history)


def allele_frequencies(genomes):
    return genomes.reshape(genomes.shape[0], -1).mean(0)

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
