import pathlib
import logging
import time


logging.basicConfig(
    format="%(asctime)s : %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
    level=logging.info,
)

logging_lines = (
    "|         " * 8 + "|",
    "|  stage  |   ETA   |   t1M   | runtime | stg/min | til mem | end mem | ",
    "| {:>7} | {:7} | {:>7} | {:>6} | {:>7} | {:>7.2f} | {:>7.2f} | ",
)
traits = ("surv", "repr", "neut", "muta")
default_cmd_arguments = {
    "params_extra": "{}",
    "jobid": "",
    "reload_deme": False,
    "config_files": [],
}
time_start = time.time()
project_path = pathlib.Path(__file__).absolute().parent.parent

### PARAMETERS
# Assigned by macroconfig.py
# TODO rethink which are simulation parameters
CYCLE_NUM = None
LOGGING_RATE = None
PICKLE_RATE = None
OVERWRITE_DIR = None
SNAPSHOT_RATE = None
VISOR_RATE = None
FLUSH_RATE = None
reload_deme = None
jobid = None
config_files = None
params_extra = None
output_path = None


### VARIABLES
stage = 0
