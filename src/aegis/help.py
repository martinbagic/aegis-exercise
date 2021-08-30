import yaml
import argparse
import logging
import pickle
import time
import numpy


from aegis.classes.reproducer import Reproducer
from aegis.classes.overshoot import Overshoot

from aegis.panconfiguration import pan


logging.basicConfig(
    format="%(asctime)s : %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S",
    level=logging.INFO,
)


def read_yml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def unpickle(path):
    with open(path, "rb") as o:
        return pickle.load(o)


def run_parsers():

    parser = argparse.ArgumentParser(description="Ageing of Evolving Genomes In Silico")
    subparsers = parser.add_subparsers()

    # Parse arguments to run the simulation
    parser_sim = subparsers.add_parser("sim", help="run simulation")
    parser_sim.add_argument(
        "custom_config_path",
        type=str,
        help="path to config file",
    )
    parser_sim.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite the output",
    )

    # Parse arguments to perform tests
    parser_test = subparsers.add_parser("test", help="Run tests")
    # parser_test.add_argument(
    #     "custom_config_path",
    #     type=str,
    #     help="path to config file",
    # )

    return parser.parse_args()


def get_params(custom_config_path):
    # Read config parameters from the custom config file
    custom_config_params = read_yml(custom_config_path)

    # Read config parameters from the default config file
    default_config_params = read_yml(
        pan.base_dir / "src" / "aegis" / "input" / "default.yml"
    )

    # Fuse
    params = {}
    params.update(default_config_params)
    params.update(custom_config_params)

    return params


def get_derived_params(params):

    jobid = f"_@{time.time()}" if params["JOBID_TIME_STAMP_"] else "_"
    random_seed = (
        numpy.random.randint(1, 10 ** 6)
        if params["RANDOM_SEED_"] == 0
        else params["RANDOM_SEED_"]
    )

    params["jobid"] = jobid
    params["random_seed"] = random_seed

    return {
        "jobid": jobid,
        "random_seed": random_seed,
    }


def validate_params(params):
    # General
    assert isinstance(params["RANDOM_SEED_"], int)

    # Runtime
    assert isinstance(params["CYCLE_NUM_"], int) and params["CYCLE_NUM_"] > 1
    assert isinstance(params["LOGGING_RATE_"], int) and params["LOGGING_RATE_"] >= 1

    # Recording
    assert isinstance(params["JOBID_TIME_STAMP_"], bool)
    assert isinstance(params["PICKLE_RATE_"], int) and params["PICKLE_RATE_"] >= 0
    assert isinstance(params["SNAPSHOT_RATE_"], int) and params["SNAPSHOT_RATE_"] >= 0
    assert isinstance(params["VISOR_RATE_"], int) and params["VISOR_RATE_"] >= 0
    assert isinstance(params["FLUSH_RATE_"], int) and params["FLUSH_RATE_"] >= 0

    # Multiple ecosystems
    assert (
        isinstance(params["ECOSYSTEM_NUMBER_"], int)
        and params["ECOSYSTEM_NUMBER_"] >= 1
    )

    # Ecology
    assert (
        isinstance(params["MAX_POPULATION_SIZE"], int)
        and params["MAX_POPULATION_SIZE"] >= 1
    )
    assert params["OVERSHOOT_EVENT"] in Overshoot.legal
    assert isinstance(params["CLIFF_SURVIVORSHIP"], bool)
    assert isinstance(params["DISCRETE_GENERATIONS"], bool)

    # Genotype
    assert isinstance(params["MAX_LIFESPAN"], int) and params["MAX_LIFESPAN"] >= 1
    assert isinstance(params["MATURATION_AGE"], int) and params["MATURATION_AGE"] >= 1
    assert isinstance(params["BITS_PER_LOCUS"], int) and (
        params["BITS_PER_LOCUS"] % 2 == 0 or params["REPR_MODE"] == "asexual"
    )
    assert isinstance(params["HEADSUP"], int) and (
        params["HEADSUP"] >= 1 or params["HEADSUP"] in (-1, 0)
    )

    # Genome structure
    # - validated when instantiating class Trait

    # Reproduction
    assert params["REPR_MODE"] in Reproducer.legal
    assert isinstance(params["RECOMBINATION_RATE"], bool)

    # Mutation
    assert params["MUTATION_RATIO"] >= 0

    # Pleiotropy
    assert isinstance(params["PLEIOTROPY_SPECS"], list)

    for triple in params["PLEIOTROPY_SPECS"]:
        assert 0 <= triple[0] < params["MAX_LIFESPAN"]  # genotype index
        assert 0 <= triple[1] < params["MAX_LIFESPAN"]  # phenotype index
        assert isinstance(triple[2], (int, float))  # weight

    # Environment
    assert (
        isinstance(params["ENVIRONMENT_CHANGE_RATE"], int)
        and params["ENVIRONMENT_CHANGE_RATE"] >= 0
    )

    # Command line arguments
    # - OK
