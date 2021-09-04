import numpy as np


class Phenomap:
    """Functional phenomap class"""

    def __init__(self, PHENOMAP_SPECS, pos_end):
        """Enable complex translation of genotype into phenotype."""
        # 'Locus value' x 'Contribution to phenotype' matrix

        # If no arguments are passed, this class becomes a dummy that does not do anything
        if PHENOMAP_SPECS == []:
            self.dummy = True
        else:
            self.dummy = False
            self.map_ = np.diag([1.0] * pos_end)
            for geno_i, pheno_i, weight in PHENOMAP_SPECS:
                self.map_[geno_i, pheno_i] = weight

    def __call__(self, probs):
        return probs if self.dummy else np.clip(probs.dot(self.map_), 0, 1)
