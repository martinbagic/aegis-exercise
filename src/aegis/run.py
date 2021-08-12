def run(use_cmd=False, **programmatic_args):

    # Import once run() function is triggered
    from aegis.progresslog import ProgressLog
    from aegis.classes.ecosystem import Ecosystem
    from aegis.panconfiguration import pan
    from aegis.functions import get_params
    import logging

    # Put parameters into the panconfiguration
    params = get_params(use_cmd, programmatic_args)
    pan.load(params)

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
