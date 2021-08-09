import logging
import pickle
import time
import numpy as np

from class_logic.biosystem import Biosystem
from class_data.auxi import Auxi


class Aegis:
    """Project wrapper"""

    def __init__(self, use_cmd=False, **programmatic_args):
        self.time_start = time.time()
        self.logging_lines = [
            "|         " * 8 + "|",
            "|  stage  |   ETA   |   t1M   | runtime | stg/min | til mem | end mem | recpend |",
            "| {:>7} | {:7} | {:>7} | {:>6} | {:>7} | {:>7.2f} | {:>7.2f} | {:>7} |",
        ]

        self.auxi = Auxi(use_cmd, programmatic_args)

    def __call__(self):
        """List of all steps to perform"""
        self.biosystem = self.get_biosystem()
        self.start_simulation()
        self.run_simulation()
        self.end_simulation()

    def get_biosystem(self):
        """Initialize biosystem"""

        if self.auxi.reload_biosystem:
            logging.debug(f"Reloading biosystem from: {self.auxi.reload_biosystem}")
            with open(
                self.auxi.project_path / "output" / self.auxi.reload_biosystem, "rb"
            ) as ifile:
                pop = pickle.load(ifile).pop
                biosystem = Biosystem(pop=pop, auxi=self.auxi)
        else:
            logging.debug("Initializing biosystem afresh")
            biosystem = Biosystem(auxi=self.auxi)

        return biosystem

    def start_simulation(self):
        """Steps before running the core simulation"""

        logging.debug("Simulation started")
        logging.debug(self.logging_lines[1])

    def run_simulation(self):
        """Core simulation"""

        def get_memory_usage(path):
            total_memory_usage = (
                sum(f.stat().st_size for f in path.glob("*") if f.is_file())
                / 1024
                / 1024
                / 1024
            )  # GB
            return total_memory_usage

        def get_time_estimations(stage, CYCLE_NUM):
            def get_dhm(timediff):
                d = int(timediff / 86400)
                timediff %= 86400
                h = int(timediff / 3600)
                timediff %= 3600
                m = int(timediff / 60)
                return f"{d}`{h:02}:{m:02}"

            time_diff = time.time() - self.time_start

            seconds_per_100 = time_diff / stage * 100
            eta = (CYCLE_NUM - stage) / 100 * seconds_per_100

            stages_per_min = int(stage / (time_diff / 60))

            runtime = get_dhm(time_diff)
            time_per_1M = get_dhm(time_diff / stage * 1000000)
            eta = get_dhm(eta)

            return eta, time_per_1M, runtime, stages_per_min

        for _ in range(self.auxi.CYCLE_NUM):

            self.auxi.stage += 1

            # Check if time to save Visor data
            if self.auxi.stage % self.auxi.recorder.JSON_RATE == 0:
                self.auxi.recorder.rec_json_flag = True

            # Check if time to save Counter data
            if self.auxi.stage % self.auxi.counter.rate == 0:
                self.auxi.counter.flush(self.biosystem.pop)

            # Check if time to save detailed data
            if (
                self.auxi.stage
                % (self.auxi.recorder.JSON_RATE * self.auxi.recorder.REC_RATE)
                == 0
            ):
                self.auxi.recorder.rec_flush_flag = True

            # Perform one simulation core cycle
            self.biosystem.cycle()

            # Check if population is extinct
            if len(self.biosystem) == 0:
                logging.debug("Biosystem went extinct")
                self.auxi.recorder.visor_data["extinct"] = True  # record going extinct
                break

            # Print logging headers every 10 logging lines
            if self.auxi.stage % (self.auxi.LOGGING_RATE * 10) == 0:
                logging.debug(self.logging_lines[0])
                logging.debug(self.logging_lines[1])

            # Emit logging line
            if self.auxi.stage % self.auxi.LOGGING_RATE == 0:
                eta, sper1M, runtime, stpermin = get_time_estimations(
                    self.auxi.stage, self.auxi.CYCLE_NUM
                )
                til_memory_use = get_memory_usage(self.auxi.recorder.opath)
                end_memory_use = (
                    (self.auxi.CYCLE_NUM - self.auxi.stage)
                    / self.auxi.stage
                    * til_memory_use
                )

                logging.info(
                    self.logging_lines[2].format(
                        self.auxi.stage,
                        eta,
                        sper1M,
                        runtime,
                        stpermin,
                        til_memory_use,
                        end_memory_use,
                        len(self.auxi.recorder.genomes),
                    )
                )

    def end_simulation(self):
        """Steps after running the core simulation"""

        # Pickle the current population
        # self.auxi.recorder.pickle_pop(self.biosystem, self.auxi.stage)
        # TODO fix pickling

        # Kill the current population
        mask_kill = np.ones(len(self.biosystem.pop), bool)
        self.biosystem._kill(mask_kill, "end_of_sim")

        # Write out the remaining data
        self.auxi.recorder.save(force=True)
        self.auxi.recorder.write_to_visor()

        logging.debug("Simulation finished")
