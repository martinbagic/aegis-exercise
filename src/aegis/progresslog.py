import numpy as np
import time
import logging

from aegis.panconfiguration import pan


class ProgressLog:
    """Log runtime statistics (e.g. estimated time until completion)"""

    header = ["stage", "ETA", "t1M", "runtime", "stg/min"]

    def __init__(self):

        self.path = pan.jobid_path / "progress.log"

        with open(self.path, "ab") as f:
            np.savetxt(f, [self.header], fmt="%-10s", delimiter="| ")

    def log(self):
        if pan.skip(pan.LOGGING_RATE_):
            return
        logging.info(f"{pan.stage:8} / {pan.CYCLE_NUM_}")
        eta, sper1M, runtime, stgmin = self.get_time_estimations()

        content = (
            pan.stage,
            eta,
            sper1M,
            runtime,
            stgmin,
        )
        with open(self.path, "ab") as f:
            np.savetxt(f, [content], fmt="%-10s", delimiter="| ")

    def get_time_estimations(self):
        def get_dhm(timediff):
            d = int(timediff / 86400)
            timediff %= 86400
            h = int(timediff / 3600)
            timediff %= 3600
            m = int(timediff / 60)
            return f"{d}`{h:02}:{m:02}"

        time_diff = time.time() - pan.time_start

        seconds_per_100 = time_diff / pan.stage * 100
        eta = (pan.CYCLE_NUM_ - pan.stage) / 100 * seconds_per_100

        stages_per_min = int(pan.stage / (time_diff / 60))

        runtime = get_dhm(time_diff)
        time_per_1M = get_dhm(time_diff / pan.stage * 1000000)
        eta = get_dhm(eta)

        return eta, time_per_1M, runtime, stages_per_min
