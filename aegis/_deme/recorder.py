import pandas as pd
import numpy as np
import pickle
import json
import time
import logging

from aegis import PAN

# TODO maybe don't record phenotypic data, instead transform the genotypic data to phenotypic when necessary
# TODO remove old recorder stuff from other modules
# TODO rethink which parameters are passed to which classes

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

    def __init__(self, output_path, MAX_LIFESPAN):
        # Define output paths and make necessary directories
        self.paths = {
            "BASE_DIR": output_path,
            "pickles": output_path / "pickles",
            "snapshots_genotypes": output_path / "snapshots" / "genotypes",
            "snapshots_phenotypes": output_path / "snapshots" / "phenotypes",
            "snapshots_demography": output_path / "snapshots" / "demography",
            "visor": output_path / "visor",
            "visor_spectra": output_path / "visor" / "spectra",
        }

        for path in self.paths.values():
            path.mkdir(exist_ok=True, parents=True)

        # Needed for the second recording method
        self.MAX_LIFESPAN = MAX_LIFESPAN
        self._init_collection()

        # Needed for output summary
        self.extinct = False

    def _skip(self, rate):
        """Check whether you should skip recording"""
        # Do not record if rate is set to 0 or if stage is not a multiple of rate
        return (rate <= 0) or (PAN.stage % rate > 0)

    ### RECORDING METHOD I. (snapshots) ###

    def record_input_summary(self, input_summary):
        with open(self.paths["BASE_DIR"] / "input_summary.json", "w") as f:
            json.dump(input_summary, f, indent=4)

    def record_pickle(self, obj):
        """Pickle given population"""
        if self._skip(PAN.PICKLE_RATE):
            return
        with open(self.paths["pickles"] / str(PAN.stage), "wb") as ofile:
            pickle.dump(obj, ofile)

    def record_visor(self, pop):
        if self._skip(PAN.VISOR_RATE):
            return

        # genotypes.csv | Record allele frequency
        with open(self.paths["visor"] / "genotypes.csv", "ab") as f:
            array = pop.genomes.reshape(len(pop), -1).mean(0).reshape(1, -1)
            np.savetxt(f, array, delimiter=",", fmt="%1.3e")

        # phenotypes.csv | Record median phenotype
        with open(self.paths["visor"] / "phenotypes.csv", "ab") as f:
            array = np.median(pop.phenotypes, 0).reshape(1, -1)
            np.savetxt(f, array, delimiter=",", fmt="%1.3e")

        self.flush()

    def record_snapshots(self, pop):
        if self._skip(PAN.SNAPSHOT_RATE):
            return

        # genotypes
        df_gen = pd.DataFrame(np.array(pop.genomes.reshape(len(pop), -1)))
        df_gen.reset_index(drop=True, inplace=True)
        df_gen.columns = [str(c) for c in df_gen.columns]
        df_gen.to_feather(self.paths["snapshots_genotypes"] / f"{PAN.stage}.feather")

        # phenotypes
        df_phe = pd.DataFrame(np.array(pop.phenotypes))
        df_phe.reset_index(drop=True, inplace=True)
        df_phe.columns = [str(c) for c in df_phe.columns]
        df_phe.to_feather(self.paths["snapshots_phenotypes"] / f"{PAN.stage}.feather")

        # demography
        dem_attrs = ["ages", "births", "birthdays"]
        demo = {attr: getattr(pop, attr) for attr in dem_attrs}
        df_dem = pd.DataFrame(demo, columns=dem_attrs)
        df_dem.reset_index(drop=True, inplace=True)
        df_dem.to_feather(self.paths["snapshots_demography"] / f"{PAN.stage}.feather")

    def record_output_summary(self):
        output_summary = {
            "extinct": self.extinct,
            "TIME_START": PAN.time_start,
            "time_end": time.time(),
        }
        with open(self.paths["BASE_DIR"] / "output_summary.json", "w") as f:
            json.dump(output_summary, f, indent=4)

    ### RECORDING METHOD II. (flushes) ###

    def _init_collection(self):
        self.collection = {
            "age_at_birth": [0] * self.MAX_LIFESPAN,
            "age_at_overshoot": [0] * self.MAX_LIFESPAN,
            "age_at_genetic": [0] * self.MAX_LIFESPAN,
            "cumulative_ages": [0] * self.MAX_LIFESPAN,
            "age_at_end_of_sim": [0] * self.MAX_LIFESPAN,
        }

    def collect(self, key, ages):
        for age in ages:
            self.collection[key][age - 1] += 1  # age == index + 1

    def flush(self):
        # spectra/*.csv | Age distribution of various subpopulations (e.g. population that died of genetic causes)
        for key, val in self.collection.items():
            with open(self.paths["visor_spectra"] / f"{key}.csv", "ab") as f:
                array = np.array(val).reshape(1, -1)
                np.savetxt(f, array, delimiter=",", fmt="%i")

        # Reinitialize the collection
        self._init_collection()


class Stats:
    pass
