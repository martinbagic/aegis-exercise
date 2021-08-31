import numpy as np


class Phenomap:
    """Functional phenomap class"""

    def __init__(self, PHENOMAP_SPECS=None, pos_end=None):
        # 'Locus value' x 'Contribution to phenotype' matrix

        if PHENOMAP_SPECS is None and pos_end is None:
            self.fake = True
        else:
            self.fake = False
            self.map_ = np.diag([1.0] * pos_end)
            for geno_i, pheno_i, weight in PHENOMAP_SPECS:
                self.map_[geno_i, pheno_i] = weight

    def __call__(self, probs):
        return probs if self.fake else np.clip(probs.dot(self.map_), 0, 1)
