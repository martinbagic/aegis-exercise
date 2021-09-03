def validate_keys(params, legal_keys):
    for key in params:
        assert key in legal_keys, f"'{key}' is not a legal parameter"


def validate_values(params):
    # General
    assert isinstance(params["RANDOM_SEED_"], (int, type(None)))

    # Runtime
    assert (
        isinstance(params["STAGES_PER_SIMULATION_"], int)
        and params["STAGES_PER_SIMULATION_"] >= 1
    )
    assert isinstance(params["LOGGING_RATE_"], int) and params["LOGGING_RATE_"] >= 0

    # Recording
    assert isinstance(params["SNAPSHOT_RATE_"], int) and params["SNAPSHOT_RATE_"] >= 0
    assert isinstance(params["VISOR_RATE_"], int) and params["VISOR_RATE_"] >= 0

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
    assert (
        isinstance(params["CLIFF_SURVIVORSHIP"], (type(None), float))
        and 0 < params["CLIFF_SURVIVORSHIP"] < 1
    )
    assert isinstance(params["STAGES_PER_SEASON"], int)

    # Genotype
    assert isinstance(params["MAX_LIFESPAN"], int) and params["MAX_LIFESPAN"] >= 1
    assert isinstance(params["MATURATION_AGE"], int) and params["MATURATION_AGE"] >= 1
    assert isinstance(params["BITS_PER_LOCUS"], int)
    assert isinstance(params["HEADSUP"], int) and (
        params["HEADSUP"] >= 1 or params["HEADSUP"] in (-1, 0)
    )

    # Genome structure
    # - validated when instantiating class Trait

    # Reproduction
    assert params["REPRODUCTION_MODE"] in (
        "sexual",
        "asexual",
        "asexual_diploid",
    )
    assert isinstance(params["RECOMBINATION_RATE"], (bool, float))

    # Mutation
    assert (
        isinstance(params["MUTATION_RATE"], (int, float))
        and params["MUTATION_RATIO"] >= 0
    )

    # Phenomap
    assert isinstance(params["PHENOMAP_SPECS"], list)

    for triple in params["PHENOMAP_SPECS"]:
        assert 0 <= triple[0] < params["MAX_LIFESPAN"]  # genotype index
        assert 0 <= triple[1] < params["MAX_LIFESPAN"]  # phenotype index
        assert isinstance(triple[2], (int, float))  # weight

    # Environment
    assert (
        isinstance(params["ENVIRONMENT_CHANGE_RATE"], int)
        and params["ENVIRONMENT_CHANGE_RATE"] >= 0
    )
