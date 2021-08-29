"""
Parameter source priority:
    1. programmatic_params: Programmatic
    2. cmd_params: extra parameters from the command line
    3. config_params: config files specified in the command line; first item has highest priority, each subsequent item has lower priority; e.g. `--config_files config1 config2 config3` causes the parameters from config1 to override those from config2, etc.
    4. config_params: _DEFAULT config file; default item added to the end of the list
"""

import yaml
import logging
import argparse
import time
import numpy

import pickle

from aegis.classes.reproducer import Reproducer
from aegis.classes.overshoot import Overshoot
from aegis.panconfiguration import pan

logging.basicConfig(
    format="%(asctime)s : %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
    level=logging.INFO,
)

# TODO how to use input_summary.json to start a new simulation
# TODO multiple populations
# TODO test whether panconfiguration works with multiple aegis processes run

# TODO perform warnings when passing information to aegis which isnt used because unpickling is enabled
# TODO pickle only the Population and the Environment


def get_params(use_cmd, programmatic_params):
    """Extract parameters from multiple sources, document all and combine into final"""

    default_cmd_parameters = {
        "output_path": "aegis_output/",
        "config_files": [],
        "extra_params": [],
        "unpickle_jobid": False,
        "jobid": "_",
    }

    def get_cmd_params():
        """Parse and process arguments from the command line"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-o",
            "--output_path",
            type=str,
            default=default_cmd_parameters["output_path"],
            help="relative path to folder in which the parent folder with output data will be created",
        )
        parser.add_argument(
            "-e",
            "--extra_params",
            type=str,
            nargs="*",
            default=default_cmd_parameters["extra_params"],
            help="list of extra parameters that override config parameters",
        )
        parser.add_argument(
            "--jobid",
            type=str,
            default=default_cmd_parameters["jobid"],
            help="name of the parent folder that will contain all output data"
        )
        parser.add_argument(
            "-r",
            "--unpickle_jobid",
            type=bool,
            default=default_cmd_parameters["unpickle_jobid"],
            help="use a pickle file to start the simulation from a pre-evolved simulation"
        )
        parser.add_argument(
            "-c",
            "--config_files",
            nargs="*",
            type=str,
            default=default_cmd_parameters["config_files"],
            help="list of config files that override default parameters"
        )
        return vars(parser.parse_args())

    def get_config_params(custom_config_files):

        # Read config parameters from custom config files
        custom_config_params = [
            read_yml(pan.base_dir / "src" / "input" / custom_config_file)
            for custom_config_file in custom_config_files
        ]

        # Read config parameters from the default config file
        default_config_params = [
            read_yml(pan.base_dir / "src" / "aegis" / "input" / "default.yml")
        ]

        # Join lists and invert (to respect priority)
        params_lists = (custom_config_params + default_config_params)[
            ::-1
        ]  # [::-1] because the last item has the lowest priority

        # Combine config parameters
        config_params = {}
        for params_item in params_lists:
            config_params.update(params_item)

        return config_params

    def get_extra_params(extras, config_params):
        # Unpack extra parameters and change type from string to other, appropriate type

        extra_params = dict()
        for estring in extras:
            assert estring.count("=") == 1
            key, val = estring.split("=")
            assert key in config_params, "Key of the extra parameter is not valid"
            # TODO do not copy types from config_params
            param_type = type(config_params[key])
            if param_type == bool:
                val = val == "True"
            else:
                val = param_type(val)

            extra_params[key] = val  # Change type of v using the established types
        return extra_params

    def validate_params(params):
        # General
        assert isinstance(params["RANDOM_SEED_"], int)

        # Runtime
        assert isinstance(params["CYCLE_NUM_"], int) and params["CYCLE_NUM_"] > 1
        assert isinstance(params["LOGGING_RATE_"], int) and params["LOGGING_RATE_"] >= 1

        # Recording
        assert isinstance(params["JOBID_TIME_STAMP_"], bool)
        assert isinstance(params["PICKLE_RATE_"], int) and params["PICKLE_RATE_"] >= 0
        assert (
            isinstance(params["SNAPSHOT_RATE_"], int) and params["SNAPSHOT_RATE_"] >= 0
        )
        assert isinstance(params["VISOR_RATE_"], int) and params["VISOR_RATE_"] >= 0
        assert isinstance(params["FLUSH_RATE_"], int) and params["FLUSH_RATE_"] >= 0

        # Multiple ecosystems
        assert (
            isinstance(params["ECOSYSTEM_NUMBER_"], int)
            and params["ECOSYSTEM_NUMBER_"] >= 1
        )

        # Ecology
        assert (
            isinstance(params["MAX_POPULATION_SIZE"], int)
            and params["MAX_POPULATION_SIZE"] >= 1
        )
        assert params["OVERSHOOT_EVENT"] in Overshoot.legal
        assert isinstance(params["CLIFF_SURVIVORSHIP"], bool)
        assert isinstance(params["DISCRETE_GENERATIONS"], bool)

        # Genotype
        assert isinstance(params["MAX_LIFESPAN"], int) and params["MAX_LIFESPAN"] >= 1
        assert (
            isinstance(params["MATURATION_AGE"], int) and params["MATURATION_AGE"] >= 1
        )
        assert isinstance(params["BITS_PER_LOCUS"], int) and (
            params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"
        )
        assert isinstance(params["HEADSUP"], int) and (
            params["HEADSUP"] >= 1 or params["HEADSUP"] in (-1, 0)
        )

        # Genome structure
        # - validated when instantiating class Trait

        # Reproduction
        assert params["REPR_MODE"] in Reproducer.legal
        assert isinstance(params["RECOMBINATION_RATE"], bool)

        # Mutation
        assert params["MUTATION_RATIO"] >= 0

        # Pleiotropy
        assert isinstance(params["PLEIOTROPY_SPECS"], list)

        for triple in params["PLEIOTROPY_SPECS"]:
            assert 0 <= triple[0] < params["MAX_LIFESPAN"]  # genotype index
            assert 0 <= triple[1] < params["MAX_LIFESPAN"]  # phenotype index
            assert isinstance(triple[2], (int, float))  # weight

        # Environment
        assert (
            isinstance(params["ENVIRONMENT_CHANGE_RATE"], int)
            and params["ENVIRONMENT_CHANGE_RATE"] >= 0
        )

        # Command line arguments
        # - OK

    def validate_programmatic_params(programmatic_params):
        legal_types = read_yml(pan.base_dir / "src/aegis/input/legal_types.yml")

        for param_name, param_value in programmatic_params.items():
            assert param_name in legal_types.keys(), f"{param_name} is not a legal key"
            assert (
                type(param_value).__name__ == legal_types[param_name]
            ), f"{param_name} is type {type(param_value).__name__}, but it should be {legal_types[param_name]}"

    ### GET ALL PARAMETERS

    # priority 1: PROGRAM CALL
    validate_programmatic_params(programmatic_params)

    # N/A: COMMAND LINE
    cmd_params = get_cmd_params() if use_cmd else default_cmd_parameters

    # priority 3: CONFIG FILES (custom and default)
    config_params = get_config_params(cmd_params["config_files"])

    # priority 2: EXTRA PARAMETERS FROM COMMAND LINE
    # TODO use legal types?
    extra_params = get_extra_params(cmd_params["extra_params"], config_params)

    # TODO type(True)("False") evaluates to True; problem with extra parameters!!!

    ### PROCESS ALL PARAMETERS

    # Combine parameters respecting the priorities (from lowest to highest)
    final_params = dict()
    final_params.update(config_params)
    final_params.update(extra_params)
    final_params.update(programmatic_params)

    # Add jobid, config_files, and unpickle_jobid from programmatic_params

    final_params["output_path"] = (
        programmatic_params["output_path"]
        if "output_path" in programmatic_params
        else cmd_params["output_path"]
    )

    final_params["unpickle_jobid"] = (
        programmatic_params["unpickle_jobid"]
        if "unpickle_jobid" in programmatic_params
        else cmd_params["unpickle_jobid"]
    )

    final_params["config_files"] = (
        programmatic_params["config_files"]
        if "config_files" in programmatic_params
        else cmd_params["config_files"]
    )

    jobid = (
        programmatic_params["jobid"]
        if "jobid" in programmatic_params
        else cmd_params["jobid"]
    )
    if final_params["JOBID_TIME_STAMP_"]:
        jobid += f"@{time.time()}"
    final_params["jobid"] = jobid

    # Randomize RANDOM_SEED_ if == 0
    if final_params["RANDOM_SEED_"] == 0:
        final_params["RANDOM_SEED_"] = numpy.random.randint(1, 10 ** 6)

    # Document all params
    final_params["_sources"] = {
        "programmatic_params": programmatic_params,
        "cmd_params": cmd_params,
        "extra_params": extra_params,
        "config_params": config_params,
    }

    # TODO do not use programmatic params (it is only used for testing!)
    # TODO Validate that programmatic_params exist
    # TODO validate all parameters, check which parameters are coming from where

    # Validate parameters
    validate_params(final_params)

    logging.info(f"Final validated parameters: {final_params}")

    return final_params


def unpickle(path):
    with open(path, "rb") as o:
        return pickle.load(o)


def read_yml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)
