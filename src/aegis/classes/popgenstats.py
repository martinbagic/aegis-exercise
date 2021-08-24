from statistics import harmonic_mean


class PopgenStats:
    def __init__(self):
        pass

    def analyze(self, population):
        """Calculate and return population genetic statistics"""

        def pop_size():
            return population.pop_size_history[-1]

        def pop_size_effective():
            return harmonic_mean(population.pop_size_history)

        return (pop_size(), pop_size_effective())
