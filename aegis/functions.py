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

import pickle

from aegis.classes.deme import Deme
from aegis.progresslog import ProgressLog
from aegis.panconfiguration import pan


logging.basicConfig(
    format="%(asctime)s : %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
    level=logging.info,
)

# TODO how to use input_summary.json to start a new simulation
# TODO multiple populations
# TODO test whether panconfiguration works with multiple aegis processes run

# TODO perform warnings when passing information to aegis which isnt used because unpickling is enabled
# TODO pickle only the Population


def run(use_cmd, **programmatic_args):

    params = get_params(use_cmd, programmatic_args)

    pan.load_from_params(params)

    demes = [Deme(params)]

    progresslog = ProgressLog()

    assert len(demes) == len(
        set(deme.deme_id for deme in demes)
    ), "Assert deme_id uniqueness"

    logging.info("Simulation started")

    while pan.stage < pan.CYCLE_NUM_:
        pan.stage += 1
        for deme in demes:
            deme.cycle()
        progresslog.log()

    logging.info("Simulation finished")


def get_params(use_cmd, programmatic_params):
    # Get parameters
    def get_cmd_params():

        """Parse and process arguments from the command line"""

        if use_cmd:
            # Fetch arguments
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--params_extra",
                type=str,
                default=pan.default_cmd_arguments["params_extra"],
            )
            parser.add_argument(
                "--jobid",
                type=str,
                default=pan.default_cmd_arguments["jobid"],
            )
            parser.add_argument(
                "-r",
                "--unpickle_jobid",
                type=str,
                default=pan.default_cmd_arguments["unpickle_jobid"],
            )
            parser.add_argument(
                "-c",
                "--config_files",
                nargs="*",
                type=str,
                default=pan.default_cmd_arguments["config_files"],
            )
            args = parser.parse_args()
        else:
            args = pan.default_cmd_arguments

        # Process arguments
        args["config_files"].append("_DEFAULT.yml")
        if args["jobid"] == "":
            # [0] because name job according to highest-priority config file
            # .split()[0] because you want to remove ".yml"
            args["jobid"] = args["config_files"][0].split()[0]

        return args

    def get_config_params():
        def find_config_file(config_file):
            """Find the config file either in config_preset/ or config_custom/"""
            for folder in ("config_preset", "config_custom"):
                path = pan.base_dir / "input" / folder / config_file
                if path.is_file():
                    return path

        def read_config_file(path):
            with open(path, "r") as ifile:
                return yaml.safe_load(ifile)

        config_params = {}

        # Add parameters from config files
        for config_file in cmd_params["config_files"]:
            path_config = find_config_file(config_file)
            config_params = {**read_config_file(path_config), **config_params}
        return config_params

    programmatic_params = programmatic_params  # priority 1
    cmd_params = get_cmd_params()  # priority 2
    config_params = get_config_params()  # priority 3 and 4

    # Combine parameters
    params = dict()
    params.update(config_params)
    params.update(cmd_params)
    params.update(programmatic_params)

    # Validate parameters
    assert params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"

    return params


def unpickle(path):
    with open(path, "rb") as o:
        return pickle.load(o)
