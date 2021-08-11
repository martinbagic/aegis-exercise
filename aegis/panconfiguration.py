import pathlib
import time
import shutil
import logging

# TODO migration: add a parameter that determines the magnetism with which a deme attracts other individuals


class Panconfiguration:

    traits = ("surv", "repr", "neut", "muta")
    default_cmd_arguments = {
        "params_extra": "{}",
        "jobid": "",
        "unpickle_jobid": False,
        "config_files": [],
    }
    base_dir = pathlib.Path(__file__).absolute().parent.parent

    ### PARAMETERS # assigned by functions.py
    CYCLE_NUM_ = None
    LOGGING_RATE_ = None
    OVERWRITE_DIR_ = None
    PICKLE_RATE_ = None
    SNAPSHOT_RATE_ = None
    VISOR_RATE_ = None
    FLUSH_RATE_ = None
    DEME_NUMBER_ = None

    ### DERIVED PARAMETERS
    jobid_path = None
    stage_cumulative = None  # Number of stages from the first (not pickled) version

    def __init__(self):
        self.time_start = time.time()
        self.stage = 0

    def load_from_pickle(self, pickled_pan, jobid):
        """Load parameters from a pickled pan"""
        self.DEME_NUMBER_ = pickled_pan.DEME_NUMBER_
        self.CYCLE_NUM_ = pickled_pan.CYCLE_NUM_
        self.LOGGING_RATE_ = pickled_pan.LOGGING_RATE_
        self.PICKLE_RATE_ = pickled_pan.PICKLE_RATE_
        self.OVERWRITE_DIR_ = pickled_pan.OVERWRITE_DIR_
        self.SNAPSHOT_RATE_ = pickled_pan.SNAPSHOT_RATE_
        self.VISOR_RATE_ = pickled_pan.VISOR_RATE_
        self.FLUSH_RATE_ = pickled_pan.FLUSH_RATE_

        self._set_jobid_path("jobid")

    def load_from_params(self, params):
        """Load parameters from params"""
        self.DEME_NUMBER_ = params["DEME_NUMBER_"]
        self.CYCLE_NUM_ = params["CYCLE_NUM_"]
        self.LOGGING_RATE_ = params["LOGGING_RATE_"]
        self.PICKLE_RATE_ = params["PICKLE_RATE_"]
        self.OVERWRITE_DIR_ = params["OVERWRITE_DIR_"]
        self.SNAPSHOT_RATE_ = params["SNAPSHOT_RATE_"]
        self.VISOR_RATE_ = params["VISOR_RATE_"]
        self.FLUSH_RATE_ = params["FLUSH_RATE_"]

        self._set_jobid_path(params["jobid"])

    def skip(self, rate):
        """Should you skip an action performed at a certain rate"""
        return (rate <= 0) or (self.stage % rate > 0)

    def _set_jobid_path(self, jobid):
        jobid_path = pan.base_dir / "output" / jobid
        if self.OVERWRITE_DIR_:
            shutil.rmtree(jobid_path, ignore_errors=True)
            self.jobid_path = jobid_path
        else:
            self.jobid_path = pan.base_dir / "output" / f"{jobid}_{time.time()}"
        self.jobid_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using jobid_path '{pan.jobid_path}'")


# Initialize empty Panconfiguration which can then be populated by parameters
pan = Panconfiguration()
