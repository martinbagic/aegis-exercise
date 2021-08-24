import numpy as np


class Population:
    """Wrapper for all population data"""

    attrs = (
        "genomes",
        "ages",
        "origins",
        "uids",
        "births",
        "birthdays",
        "phenotypes"
    )

    def __init__(self, genomes, ages, origins, uids, births, birthdays, phenotypes):
        self.genomes = genomes
        self.ages = ages
        self.origins = origins
        self.uids = uids
        self.births = births
        self.birthdays = birthdays
        self.phenotypes = phenotypes
        self.pop_size_history = []

    def __len__(self):
        """Return the number of living individuals"""
        n = len(self.genomes)
        assert all(len(getattr(self, attr)) == n for attr in self.attrs), " ".join(
            (str(len(getattr(self, attr))) for attr in self.attrs)
        )
        return n

    def __getitem__(self, index):
        """Return a subpopulation"""
        return Population(
            genomes=self.genomes[index],
            ages=self.ages[index],
            origins=self.origins[index],
            uids=self.uids[index],
            births=self.births[index],
            birthdays=self.birthdays[index],
            phenotypes=self.phenotypes[index],
        )

    def __imul__(self, index):
        """Redefine itself as its own subpopulation"""
        for attr in self.attrs:
            setattr(self, attr, getattr(self, attr)[index])
        return self

    def __iadd__(self, population):
        """Merge with another population"""
        for attr in self.attrs:
            val = np.concatenate([getattr(self, attr), getattr(population, attr)])
            setattr(self, attr, val)
        return self

    def step(self):
        self.pop_size_history.append(len(self))
        return
