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
import shutil

from aegis import PAN

# TODO how to use input_summary.json to start a new simulation
# TODO multiple populations


def get_params(use_cmd, programmatic_params):

    # TODO consider setting macroconfig as a global module
    # setattr(PAN, "macroconfig", self)

    ### LOAD PARAMETERS ###

    # Get parameters
    def get_cmd_params():

        """Parse and process arguments from the command line"""

        if use_cmd:
            # Fetch arguments
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--params_extra",
                type=str,
                default=PAN.default_cmd_arguments["params_extra"],
            )
            parser.add_argument(
                "--jobid",
                type=str,
                default=PAN.default_cmd_arguments["jobid"],
            )
            parser.add_argument(
                "-r",
                "--reload_deme",
                type=str,
                default=PAN.default_cmd_arguments["reload_deme"],
            )
            parser.add_argument(
                "-c",
                "--config_files",
                nargs="*",
                type=str,
                default=PAN.default_cmd_arguments["config_files"],
            )
            args = parser.parse_args()
        else:
            args = PAN.default_cmd_arguments

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
                path = PAN.project_path / "input" / folder / config_file
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

    # Log parameters
    # logging.info("FINAL PARAMETERS:")
    # for k, v in params.items():
    #     logging.info(f"  {k:>20} = {v}")

    # Validate parameters
    assert params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"

    ### DISTRIBUTE PARAMETERS ###

    # Simulation-wide parameters; assign to PAN
    PAN.CYCLE_NUM = params["CYCLE_NUM"]
    PAN.LOGGING_RATE = params["LOGGING_RATE"]
    PAN.PICKLE_RATE = params["PICKLE_RATE"]
    PAN.OVERWRITE_DIR = params["OVERWRITE_DIR"]
    PAN.SNAPSHOT_RATE = params["SNAPSHOT_RATE"]
    PAN.VISOR_RATE = params["VISOR_RATE"]
    PAN.FLUSH_RATE = params["FLUSH_RATE"]
    PAN.reload_deme = params["reload_deme"]
    PAN.jobid = params["jobid"]
    PAN.config_files = params["config_files"]
    PAN.params_extra = params["params_extra"]

    # Simulation-wide derived parameters; assign to PAN
    def get_output_path():
        output_path = PAN.project_path / "output" / params["jobid"]
        if params["OVERWRITE_DIR"]:
            shutil.rmtree(output_path, ignore_errors=True)
        else:
            i = 1
            while output_path.is_dir():
                logging.info(f"output_path '{output_path}' already exists")
                output_path = PAN.project_path / "output" / (params["jobid"] + f"^{i}")
                i += 1
        logging.info(f"Using output_path '{output_path}'")
        return output_path

    PAN.output_path = get_output_path()

    return params
