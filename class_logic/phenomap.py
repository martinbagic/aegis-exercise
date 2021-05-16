"""Classes for simulating pleiotropy"""

import numpy as np


class Phenomap:
    """Functional pleiotropy class"""

    def __init__(self, PHENOMAP_PLUS, pos_end):
        # 'Locus value' x 'Contribution to phenotype' matrix
        self.map_ = np.diag([1.0] * pos_end)
        for geno_i, pheno_i, weight in PHENOMAP_PLUS:
            self.map_[geno_i, pheno_i] = weight

    def __call__(self, probs):
        """Multiply locus values with the matrix, sum for each trait and cap to values in [0,1]"""
        return np.clip(probs.dot(self.map_), 0, 1)


class PhenomapFake:
    """The class to call when phenomapping is disabled"""

    def __call__(self, probs):
        """Return locus values as final phenotype values"""
        return probs
