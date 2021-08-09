"""
Parameter source priority:
    1. programmatic_params: Programmatic
    2. cmd_params: extra parameters from the command line
    3. config_params: config files specified in the command line; first item has highest priority, each subsequent item has lower priority; e.g. `--config_files config1 config2 config3` causes the parameters from config1 to override those from config2, etc.
    4. config_params: _DEFAULT config file; default item added to the end of the list
"""

import yaml
import logging
import pathlib
import argparse

from class_data.recorder import Recorder, Counter
from class_data.config import Config


logging.basicConfig(
    format="%(asctime)s : %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
    level=logging.DEBUG,
)

default_args = {
    "params_extra": "{}",
    "jobid": "",
    "reload_biosystem": False,
    "config_files": [],
}


class Auxi:
    """Wrapper for simulation-wide parameters, variables and classes"""

    project_path = pathlib.Path(__file__).absolute().parent.parent

    def get_popid(self):
        self.max_popid += 1
        return self.max_popid

    def __init__(self, use_cmd, programmatic_params):
        def get_cmd_params():

            """Parse and process arguments from the command line"""

            if use_cmd:
                # Fetch arguments
                parser = argparse.ArgumentParser()
                parser.add_argument(
                    "--params_extra", type=str, default=default_args["params_extra"]
                )
                parser.add_argument("--jobid", type=str, default=default_args["jobid"])
                parser.add_argument(
                    "-r",
                    "--reload_biosystem",
                    type=str,
                    default=default_args["reload_biosystem"],
                )
                parser.add_argument(
                    "-c",
                    "--config_files",
                    nargs="*",
                    type=str,
                    default=default_args["config_files"],
                )
                args = parser.parse_args()
            else:
                args = default_args

            # Process arguments
            args["config_files"].append("_DEFAULT.yml")
            if args["jobid"] == "":
                # name job according to highest-priority config file
                args["jobid"] = args["config_files"][0][:-4]

            return args

        def get_config_params():
            def find_config_file(cfile):
                if (self.project_path / "input" / "config_preset" / cfile).is_file():
                    return self.project_path / "input" / "config_preset" / cfile
                elif (self.project_path / "input" / "config_custom" / cfile).is_file():
                    return self.project_path / "input" / "config_custom" / cfile

            def get_params(path):
                with open(path, "r") as ifile:
                    return yaml.safe_load(ifile)

            config_params = {}

            # Add parameters from config files
            for cfile in cmd_params["config_files"]:
                path_config = find_config_file(cfile)
                config_params = {**get_params(path_config), **config_params}
            return config_params

        # Get all parameters
        programmatic_params = programmatic_params  # priority 1
        cmd_params = get_cmd_params()  # priority 2
        config_params = get_config_params()  # priority 3 and 4

        # Fuse all parameters
        params = dict()
        params.update(config_params)
        params.update(cmd_params)
        params.update(programmatic_params)

        # Log parameters
        logging.info("FINAL PARAMETERS:")
        for k, v in params.items():
            logging.info(f"  {k:>20} = {v}")

        ### VALIDATE PARAMETERS ###
        assert params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"

        ### UNPACK ###
        # Unpack simulation-wide parameters and forward biosystem-specific parameters to Config's

        # Simulation-wide parameters
        self.CYCLE_NUM = params["CYCLE_NUM"]
        self.LOGGING_RATE = params["LOGGING_RATE"]
        self.REC_EVERY_NTH = params["REC_EVERY_NTH"]
        self.PICKLE_RATE = params["PICKLE_RATE"]

        self.reload_biosystem = params["reload_biosystem"]
        self.jobid = params["jobid"]
        self.config_files = params["config_files"]
        self.params_extra = params["params_extra"]

        # Simulation-wide variables
        self.stage = 0
        self.max_popid = 0

        # Paths
        def get_rec_path():
            rec_path = self.project_path / "output" / params["jobid"]
            i = 1
            while rec_path.is_dir():
                logging.debug(f"rec_path '{rec_path}' already exists")
                rec_path = self.project_path / "output" / (params["jobid"] + f"^{i}")
                i += 1
            logging.debug(f"Using rec_path '{rec_path}'")
            return rec_path

        self.rec_path = get_rec_path()

        # TODO make function to make all folders
        self.rec_path.mkdir(parents=True, exist_ok=True)  # make folder for experiment

        # Configs
        self.configs = [Config(params)]
        config = self.configs[0]

        # Recorder
        self.recorder = Recorder(
            self.rec_path,
            params,
            config.gstruc,
            config.BITS_PER_LOCUS,
            config.MATURATION_AGE,
        )

        # Counter
        self.counter = Counter(
            self.rec_path,
            params["MAX_LIFESPAN"],
            params["COUNTER_RATE"],
            config.gstruc,
        )
