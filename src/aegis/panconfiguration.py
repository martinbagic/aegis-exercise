import pathlib
import time
import numpy
import shutil

# TODO migration: add a parameter that determines the magnetism with which a ecosystem attracts other individuals


class Panconfiguration:

    traits = ("surv", "repr", "neut", "muta")
    base_dir = pathlib.Path(__file__).absolute().parent.parent.parent
    # stage_cumulative = None  # Number of stages from the first (not pickled) version

    def __init__(self):
        self.time_start = time.time()
        self.stage = 0

    def load(self, params):
        """Load parameters from params"""
        self.ECOSYSTEM_NUMBER_ = params["ECOSYSTEM_NUMBER_"]
        self.CYCLE_NUM_ = params["CYCLE_NUM_"]
        self.LOGGING_RATE_ = params["LOGGING_RATE_"]
        self.PICKLE_RATE_ = params["PICKLE_RATE_"]
        self.JOBID_TIME_STAMP_ = params["JOBID_TIME_STAMP_"]
        self.SNAPSHOT_RATE_ = params["SNAPSHOT_RATE_"]
        self.VISOR_RATE_ = params["VISOR_RATE_"]
        self.FLUSH_RATE_ = params["FLUSH_RATE_"]
        self.POPGENSTATS_RATE_ = params["POPGENSTATS_RATE_"]

        self.unpickle_jobid = params["unpickle_jobid"]
        self.jobid = params["jobid"]

        # Set random number generator
        self.rng = numpy.random.default_rng(params["RANDOM_SEED_"])

        # Make jobid_path and the necessary directories
        self.jobid_path = pathlib.Path(params["output_path"]) / self.jobid
        if self.jobid_path.exists():
            shutil.rmtree(self.jobid_path)  # Delete previous directory if existing
        self.jobid_path.mkdir(parents=True, exist_ok=True)

    def skip(self, rate):
        """Should you skip an action performed at a certain rate"""
        return (rate <= 0) or (self.stage % rate > 0)


# Initialize empty Panconfiguration which can then be populated by parameters
pan = Panconfiguration()
