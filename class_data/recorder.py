import pandas as pd
import numpy as np
import pickle
import logging
import json


class Recorder:
    """Temporarily saves and writes data from killed individuals to files."""

    attrs = {
        "sid",
        "pid",
        "bday",
        "age",
        "causeofdeath",
        "genomes",
        "popid",
        "phenotypes",
        "births",
    }

    def __init__(
        self,
        opath,
        params,
        LOCI_POS,
        BITS_PER_LOCUS,
        MATURATION_AGE,
    ):
        self.sid = []
        self.pid = []
        self.bday = []
        self.age = []
        self.causeofdeath = []
        self.genomes = []
        self.phenotypes = []
        self.births = []
        self.popid = []

        self.batch_number = 0
        self.FLUSH_RATE = params["FLUSH_RATE"]
        self.MAX_LIFESPAN = params["MAX_LIFESPAN"]
        self.JSON_RATE = params["JSON_RATE"]
        self.REC_RATE = params["REC_RATE"]

        self.LOCI_POS = LOCI_POS
        self.BITS_PER_LOCUS = BITS_PER_LOCUS
        self.opath = opath

        self.visor_paths = [
            self.opath / "json" / f"visor.json",
            self.opath.parents[1] / "Visor" / "json" / f"{self.opath.stem}.json",
        ]

        self.feather_path = self.opath / "feather"

        (self.visor_paths[0].parent).mkdir(exist_ok=True)
        (self.visor_paths[1].parent).mkdir(exist_ok=True)
        (self.feather_path).mkdir(exist_ok=True)

        self.rec_json_flag = True
        self.rec_flush_flag = True

        self.visor_data = {
            "bitsperlocus": self.BITS_PER_LOCUS,
            "survloc": self.LOCI_POS["surv"],
            "reprloc": self.LOCI_POS["repr"],
            "lifespan": self.MAX_LIFESPAN,
            "maturationage": MATURATION_AGE,
            "gensurv": [],
            "genrepr": [],
            "phesurv": [],
            "pherepr": [],
            "death_eco": [],
            "death_gen": [],
            "death_end": [],
            "params": params,
            "extinct": False,
        }

    def rec(self, pop, causeofdeath, popid):
        """Add population data to self. Flush if too many individuals recorded."""

        if self.rec_flush_flag or self.rec_json_flag:
            # Add values to self
            self.sid.extend(pop.uids)
            self.pid.extend(pop.origins)
            self.bday.extend(pop.birthdays)
            self.age.extend(pop.ages)
            self.genomes.extend(
                pop.genomes.reshape(len(pop), -1)
            )  # Flatten each genome
            self.causeofdeath.extend([causeofdeath] * len(pop))
            self.popid.extend([popid] * len(pop))
            self.phenotypes.extend(pop.phenotypes)
            self.births.extend(pop.births)

            if len(self) > self.FLUSH_RATE:
                self.save()

    def save(self, force=False):
        def dfize():
            """Rewrite data into three pandas dataframes."""
            df_gen = pd.DataFrame(np.array(self.genomes))
            df_gen.reset_index(drop=True, inplace=True)
            df_gen.columns = [str(c) for c in df_gen.columns]

            df_phe = pd.DataFrame(np.array(self.phenotypes))
            df_phe.reset_index(drop=True, inplace=True)
            df_phe.columns = [str(c) for c in df_phe.columns]

            dem_attrs = self.attrs - {"genomes", "phenotypes"}
            demo = {attr: getattr(self, attr) for attr in dem_attrs}
            df_dem = pd.DataFrame(demo, columns=dem_attrs)
            df_dem.reset_index(drop=True, inplace=True)
            df_dem["pid"] = df_dem.pid.astype(float)
            return df_gen, df_phe, df_dem

        df_gen, df_phe, df_dem = dfize()

        if self.rec_flush_flag or force:
            self.flush(df_gen, df_phe, df_dem)

        if self.rec_json_flag or force:
            self.record_for_visor(df_gen, df_phe, df_dem)

        self.rec_flush_flag = False
        self.rec_json_flag = False

        self._reinit()  # Empty data in self
        self.batch_number += 1  # Progress batch

    def flush(self, df_gen, df_phe, df_dem):
        """Write data to *.gen and *.dem files and erase all data from self"""
        path = self.feather_path / str(self.batch_number)
        df_gen.to_feather(path.with_suffix(".gen"))
        df_phe.to_feather(path.with_suffix(".phe"))
        df_dem.to_feather(path.with_suffix(".dem"))

    def record_for_visor(self, gen, phe, dem):
        def get_bits(loci_kind, array, bitsperlocus=self.BITS_PER_LOCUS):
            pos = self.LOCI_POS[loci_kind]
            return array.iloc[:, pos[0] * bitsperlocus : pos[1] * bitsperlocus]

        def get_deaths(death_kind):
            deaths = dem[dem.causeofdeath == death_kind].age.value_counts()
            return [int(deaths.get(age, 0)) for age in range(self.MAX_LIFESPAN + 1)]

        data = {
            "gensurv": get_bits("surv", gen).mean(0).astype(float).tolist(),
            "genrepr": get_bits("repr", gen).mean(0).astype(float).tolist(),
            "phesurv": get_bits("surv", phe, 1).median(0).astype(float).tolist(),
            "pherepr": get_bits("repr", phe, 1).median(0).astype(float).tolist(),
            "death_eco": get_deaths("overshoot"),
            "death_gen": get_deaths("genetic"),
            "death_end": get_deaths("max_lifespan"),
        }

        for k, v in data.items():
            self.visor_data[k].append(v)

        self.write_to_visor()

    def write_to_visor(self):
        """Create JSON for Visor"""
        for path in self.visor_paths:
            with open(path, "w") as ofile:
                json.dump(self.visor_data, ofile)

    def pickle_pop(self, obj, stage):
        """Pickle given population"""
        logging.info(f"Pickling the population at stage {stage}.")
        path = self.opath / f"{stage}.pickle"
        with open(path, "wb") as ofile:
            pickle.dump(obj, ofile)

    def __len__(self):
        """Return number of saved individuals"""
        num = len(self.genomes)
        assert all(len(getattr(self, attr)) == num for attr in self.attrs)
        return num

    def _reinit(self):
        """Empty saved data from self"""
        for attr in self.attrs:
            setattr(self, attr, [])


class Counter:
    def __init__(self, opath, maxlifespan, rate, loci_pos):
        self.opath = opath.parents[1] / "Visor" / "counter" / f"{opath.stem}.json"
        (self.opath.parent).mkdir(exist_ok=True)

        self.maxlifespan = maxlifespan
        self.rate = rate
        self.loci_pos = loci_pos

        self.reinit()

    def reinit(self):
        self.data = {
            # "popsize": [],
            # "eggpopsize": [],
            "age_at_birth": [0] * self.maxlifespan,
            "age_at_overshoot": [0] * self.maxlifespan,
            "age_at_genetic": [0] * self.maxlifespan,
            "cumulative_ages": [0] * self.maxlifespan,
        }

    def count(self, data_key, ages):
        for age in ages:
            self.data[data_key][age - 1] += 1

    def append(self, data_key, number):
        self.data[data_key].append(number)

    def process_pop(self, pop):

        self.data["gensurv"] = (
            pop.genomes[:, self.loci_pos["surv"][0] : self.loci_pos["surv"][1]]
            .mean(0)
            .astype(float)
            .tolist()
        )
        self.data["genrepr"] = (
            pop.genomes[:, self.loci_pos["repr"][0] : self.loci_pos["repr"][1]]
            .mean(0)
            .astype(float)
            .tolist()
        )

        self.data["phesurv"] = (
            np.median(
                pop.phenotypes[:, self.loci_pos["surv"][0] : self.loci_pos["surv"][1]],
                0,
            )
            .astype(float)
            .tolist()
        )
        self.data["pherepr"] = (
            np.median(
                pop.phenotypes[:, self.loci_pos["repr"][0] : self.loci_pos["repr"][1]],
                0,
            )
            .astype(float)
            .tolist()
        )

    def flush(self, pop):

        self.process_pop(pop)

        if self.opath.is_file():
            with open(self.opath, "r") as ofile:
                previous = json.load(ofile)
        else:
            previous = []

        with open(self.opath, "w") as ofile:
            json.dump(previous + [self.data], ofile)

        self.reinit()
