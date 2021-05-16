import yaml
import logging

from class_data.recorder import Recorder, Counter
from class_data.config import Config


class Auxi:
    """Wrapper for simulation-wide parameters, variables and classes"""

    def __init__(self, paths_config, cmd_params, recpath):
        def _get_params(path):
            with open(path, "r") as ifile:
                return yaml.safe_load(ifile)

        def _check_params(params):
            """Check that input parameters are allowed"""
            assert params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"

        def _add_cmd_params(params, cmd_params):
            """Add GENOME_STRUCT and GENOME_CONST modifications such as GENOME_STRUCT_surv_1"""
            for key, val in cmd_params.items():
                if key.startswith("GENOME_STRUCT_"):
                    trait = key.split("_")[2]
                    index = int(key.split("_")[3])
                    params["GENOME_STRUCT"][trait][index] = val
                elif key.startswith("GENOME_CONST_"):
                    trait = key.split("_")[2]
                    params["GENOME_CONST"][trait] = val
                else:
                    params[key] = val
            return params

        config_params = {}
        logging.info(f"Config files: {paths_config}")
        for path_config in paths_config:
            config_params = {**_get_params(path_config), **config_params}

        params = _add_cmd_params(config_params, cmd_params)
        _check_params(params)

        logging.info(f"Final parameters: {repr(params)}")

        # Simulation parameters
        self.CYCLE_NUM = params["CYCLE_NUM"]
        self.LOGGING_RATE = params["LOGGING_RATE"]
        self.REC_EVERY_NTH = params["REC_EVERY_NTH"]
        self.PICKLE_RATE = params["PICKLE_RATE"]

        # Simulation variables
        self.stage = 0
        self.max_popid = 0

        # Configs
        self.configs = [Config(params)]
        config = self.configs[0]

        # Recorder
        self.recorder = Recorder(
            recpath,
            params,
            config.loci_pos,
            config.BITS_PER_LOCUS,
            config.MATURATION_AGE,
        )

        # Counter
        self.counter = Counter(
            recpath,
            params["MAX_LIFESPAN"],
            params["COUNTER_RATE"],
            config.loci_pos,
        )

    def get_popid(self):
        self.max_popid += 1
        return self.max_popid
