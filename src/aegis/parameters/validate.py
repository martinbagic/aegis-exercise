def validate_keys(params, legal_keys):
    for key in params:
        assert key in legal_keys, "'{key}' is not a legal parameter"


def validate_values(params):
    # TODO check that only legal params are given by the user

    # General
    assert isinstance(params["RANDOM_SEED_"], (int, type(None)))

    # Runtime
    assert isinstance(params["CYCLE_NUM_"], int) and params["CYCLE_NUM_"] > 1
    assert isinstance(params["LOGGING_RATE_"], int) and params["LOGGING_RATE_"] >= 1

    # Recording
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
    assert params["OVERSHOOT_EVENT"] in (
        "treadmill_random",
        "treadmill_boomer",
        "treadmill_zoomer",
        "cliff",
        "starvation",
    )
    assert isinstance(params["CLIFF_SURVIVORSHIP"], (bool, float))
    assert isinstance(params["DISCRETE_GENERATIONS"], (bool, int))

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
    assert params["REPR_MODE"] in (
        "sexual",
        "asexual",
        "asexual_diploid",
    )
    assert isinstance(params["RECOMBINATION_RATE"], (bool, float))

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
