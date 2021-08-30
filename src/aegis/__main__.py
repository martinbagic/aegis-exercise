"""
This script is executed when you run `python3 -m aegis`.
"""

import pathlib

from aegis.progresslog import ProgressLog
from aegis.classes.ecosystem import Ecosystem
from aegis.panconfiguration import pan

from aegis import help
import logging


##################################


parsed_args = help.run_parsers()

custom_config_path = pathlib.Path(parsed_args.custom_config_path).absolute()

params = help.get_params(custom_config_path)
help.validate_params(params)

derived_params = help.get_derived_params(params)

# Set up pan
pan.load(
    params=params, derived_params=derived_params, output_path=custom_config_path.parent
)

# Create ecosystems
ecosystems = [Ecosystem(params)]
assert len(ecosystems) == len(
    set(ecosystem.ecosystem_id for ecosystem in ecosystems)
), "Assert ecosystem_id uniqueness"

# Create progresslog
progresslog = ProgressLog()

# Run simulation
logging.info("Simulation started")
while pan.stage < pan.CYCLE_NUM_:
    pan.stage += 1
    for ecosystem in ecosystems:
        ecosystem.cycle()
    progresslog.log()
logging.info("Simulation finished")
