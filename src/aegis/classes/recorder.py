import pandas as pd
import numpy as np
import pickle
import json
import time
import copy

from aegis.panconfiguration import pan

# TODO maybe don't record phenotypic data, instead transform the genotypic data to phenotypic when necessary

# TODO phylogeny.csv Visor
# TODO stats.csv Visor


class Recorder:
    """
    Records data into output/{jobid}/ directory.

    KINDS OF OUTPUT FILES
        1. Input summary
        2. Pickle
        3. Visor data
        4. Snapshot data

    RECORDING METHODS
        I. Snapshots (record data from the population at a specific stage)
        II. Flushes (collect data over time then flush)
    """

    def __init__(self, ecosystem_id, MAX_LIFESPAN):
        # Define output paths and make necessary directories

        opath = pan.jobid_path / str(ecosystem_id)

        self.paths = {
            "BASE_DIR": opath,
            # "pickles": opath / "pickles",
            "snapshots_genotypes": opath / "snapshots" / "genotypes",
            "snapshots_phenotypes": opath / "snapshots" / "phenotypes",
            "snapshots_demography": opath / "snapshots" / "demography",
            "visor": opath / "visor",
            "visor_spectra": opath / "visor" / "spectra",
        }

        for path in self.paths.values():
            path.mkdir(exist_ok=True, parents=True)

        # Initialize collection
        self._collection = {
            "age_at_birth": [0] * MAX_LIFESPAN,
            "age_at_overshoot": [0] * MAX_LIFESPAN,
            "age_at_genetic": [0] * MAX_LIFESPAN,
            "cumulative_ages": [0] * MAX_LIFESPAN,
            "age_at_end_of_sim": [0] * MAX_LIFESPAN,
        }
        self.collection = copy.deepcopy(self._collection)

        # Needed for output summary
        self.extinct = False

    ### RECORDING METHOD I. (snapshots) ###

    def record_input_summary(self, input_summary):
        """Records aggregated parameters for a specific ecosystem"""
        with open(self.paths["BASE_DIR"] / "input_summary.json", "w") as f:
            json.dump(input_summary, f, indent=4)

    def record_pickle(self, obj):
        """Pickle given population"""
        return
        # if pan.skip(pan.PICKLE_RATE_):
        #     return
        # # with open(self.paths["pickles"] / str(pan.stage), "wb") as ofile:
        # #     pickle.dump(obj, ofile)

        # with open(self.paths["BASE_DIR"] / "ecosystem.pickle", "wb") as ofile:
        #     pickle.dump(obj, ofile)

    def record_visor(self, population):
        if pan.skip(pan.VISOR_RATE_):
            return

        # genotypes.csv | Record allele frequency
        with open(self.paths["visor"] / "genotypes.csv", "ab") as f:
            array = population.genomes.reshape(len(population), -1).mean(0)
            np.savetxt(f, [array], delimiter=",", fmt="%1.3e")

        # phenotypes.csv | Record median phenotype
        with open(self.paths["visor"] / "phenotypes.csv", "ab") as f:
            array = np.median(population.phenotypes, 0)
            np.savetxt(f, [array], delimiter=",", fmt="%1.3e")

        self.flush()

    def record_snapshots(self, population):
        if pan.skip(pan.SNAPSHOT_RATE_):
            return

        # genotypes
        df_gen = pd.DataFrame(np.array(population.genomes.reshape(len(population), -1)))
        df_gen.reset_index(drop=True, inplace=True)
        df_gen.columns = [str(c) for c in df_gen.columns]
        df_gen.to_feather(self.paths["snapshots_genotypes"] / f"{pan.stage}.feather")

        # phenotypes
        df_phe = pd.DataFrame(np.array(population.phenotypes))
        df_phe.reset_index(drop=True, inplace=True)
        df_phe.columns = [str(c) for c in df_phe.columns]
        df_phe.to_feather(self.paths["snapshots_phenotypes"] / f"{pan.stage}.feather")

        # demography
        dem_attrs = ["ages", "births", "birthdays"]
        demo = {attr: getattr(population, attr) for attr in dem_attrs}
        df_dem = pd.DataFrame(demo, columns=dem_attrs)
        df_dem.reset_index(drop=True, inplace=True)
        df_dem.to_feather(self.paths["snapshots_demography"] / f"{pan.stage}.feather")

    def record_output_summary(self):
        output_summary = {
            "extinct": self.extinct,
            "TIME_START": pan.time_start,
            "time_end": time.time(),
        }
        with open(self.paths["BASE_DIR"] / "output_summary.json", "w") as f:
            json.dump(output_summary, f, indent=4)

    ### RECORDING METHOD II. (flushes) ###

    def collect(self, key, ages):
        for age in ages:
            self.collection[key][age - 1] += 1  # age == index + 1

    def flush(self):
        # spectra/*.csv | Age distribution of various subpopulations (e.g. population that died of genetic causes)
        for key, val in self.collection.items():
            with open(self.paths["visor_spectra"] / f"{key}.csv", "ab") as f:
                array = np.array(val)
                np.savetxt(f, [array], delimiter=",", fmt="%i")

        # Reinitialize the collection
        self.collection = copy.deepcopy(self._collection)


class Stats:
    """Calculates population genetic statistics"""

    pass
