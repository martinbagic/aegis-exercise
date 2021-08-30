# When testing, use the following command:
#   `python3 -m pytest tests/ --log-cli-level=DEBUG`

import pathlib
import pandas as pd
import logging

import aegis

# TODO use a random seed in the simulation and report it in output and allow it to be specified in input

basepath_reference = pathlib.Path(__file__).absolute().parent
basepath_generated = pathlib.Path(__file__).absolute().parent.parent / "output"


def compare(filepath, path_generated, path_reference):
    df_generated = pd.read_csv(path_generated / filepath)
    df_reference = pd.read_csv(path_reference / filepath)
    pd.testing.assert_frame_equal(df_generated, df_reference)


# TODO issue running tests/ with argparse arguments


def test_basic():

    jobid = "test_basic"
    aegis.run(
        use_cmd=False,
        CYCLE_NUM_=2021,
        jobid=jobid,
        JOBID_TIME_STAMP_=False,
        config_files=[],
    )

    for filepath in (
        "genotypes.csv",
        "phenotypes.csv",
        "spectra/age_at_birth.csv",
        "spectra/age_at_end_of_sim.csv",
        "spectra/age_at_genetic.csv",
        "spectra/age_at_overshoot.csv",
        "spectra/cumulative_ages.csv",
    ):
        compare(
            filepath=filepath,
            path_generated=basepath_generated / jobid / "1/visor",
            path_reference=basepath_reference / "visor_basic",
        )


# def test_reloaded():

#     jobid = "test_reloaded"
#     run(
#         use_cmd=False,
#         CYCLE_NUM_=2021,
#         jobid=jobid,
#         OVERWRITE_DIR_=True,
#         unpickle_jobid="test_basic",
#     )

#     results = pathlib.Path().glob(f"output/{jobid}*")
#     last_result = next(results)

#     for filepath in (
#         "genotypes.csv",
#         "phenotypes.csv",
#         "spectra/age_at_birth.csv",
#         "spectra/age_at_end_of_sim.csv",
#         "spectra/age_at_genetic.csv",
#         "spectra/age_at_overshoot.csv",
#         "spectra/cumulative_ages.csv",
#     ):
#         compare(filepath=filepath, path_generated=last_result / "1" / "visor")
