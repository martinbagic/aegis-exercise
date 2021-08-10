import logging
import pickle
import time

from aegis.deme import Deme
from aegis._deme.recorder import Recorder
from aegis._deme.config import Config
from aegis import funcs
from aegis import PAN

# TODO polish recorder.py, config.py, macroconfig.py, aegis.py, tests/*.py


class Aegis:
    """Project wrapper"""

    def __init__(self, use_cmd=False, **programmatic_args):

        params = funcs.get_params(use_cmd, programmatic_args)

        self.demes = []

        # Configs
        self.configs = [Config(params)]
        config = self.configs[0]

        # Recorder
        # TODO: output path is not actually PAN
        recorder = Recorder(PAN.output_path, params["MAX_LIFESPAN"])
        recorder.record_input_summary(params)  # Record input summary

        def get_deme():
            """Initialize deme"""

            if PAN.reload_deme:
                logging.info(f"Reloading deme from: {PAN.reload_deme}")
                with open(
                    PAN.project_path / "output" / PAN.reload_deme,
                    "rb",
                ) as ifile:
                    pop = pickle.load(ifile).pop
                    deme = Deme(pop=pop, config=config, recorder=recorder)
            else:
                logging.info("Initializing deme afresh")
                deme = Deme(config=config, recorder=recorder)

            return deme

        self.deme = get_deme()
        self.start_simulation()
        self.run_simulation()
        self.end_simulation()

    def start_simulation(self):
        """Steps before running the core simulation"""

        logging.info("Simulation started")
        logging.info(PAN.logging_lines[1])

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

            time_diff = time.time() - PAN.time_start

            seconds_per_100 = time_diff / stage * 100
            eta = (CYCLE_NUM - stage) / 100 * seconds_per_100

            stages_per_min = int(stage / (time_diff / 60))

            runtime = get_dhm(time_diff)
            time_per_1M = get_dhm(time_diff / stage * 1000000)
            eta = get_dhm(eta)

            return eta, time_per_1M, runtime, stages_per_min

        for _ in range(PAN.CYCLE_NUM):

            PAN.stage += 1

            # Perform one simulation core cycle
            self.deme.cycle()

            # Check if population is extinct
            if len(self.deme) == 0:
                logging.info("Deme went extinct")
                self.deme.recorder.extinct = (
                    True  # note extinction in output summary
                )
                break

            # Print logging headers every 10 logging lines
            if PAN.stage % (PAN.LOGGING_RATE * 10) == 0:
                logging.info(PAN.logging_lines[0])
                logging.info(PAN.logging_lines[1])

            # Emit logging line
            if PAN.stage % PAN.LOGGING_RATE == 0:
                eta, sper1M, runtime, stpermin = get_time_estimations(
                    PAN.stage, PAN.CYCLE_NUM
                )
                til_memory_use = get_memory_usage(
                    self.deme.recorder.paths["BASE_DIR"]
                )
                end_memory_use = (
                    (PAN.CYCLE_NUM - PAN.stage) / PAN.stage * til_memory_use
                )

                logging.info(
                    PAN.logging_lines[2].format(
                        PAN.stage,
                        eta,
                        sper1M,
                        runtime,
                        stpermin,
                        til_memory_use,
                        end_memory_use,
                    )
                )

    def end_simulation(self):
        """Steps after running the core simulation"""
        self.deme.terminate()
        logging.info("Simulation finished")
