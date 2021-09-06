import pathlib
import pandas as pd
import pytest

base_path = pathlib.Path(__file__).absolute().parent

custom_config_files = (
    path.name
    for path in (base_path / "reference").iterdir()
    if path.name.startswith("test")
)


@pytest.mark.parametrize("conf", custom_config_files)
def test_scenario(conf):
    path_generated = base_path / "generated" / conf
    path_reference = base_path / "reference" / conf


    def compare_csv(subpath):
        df_generated = pd.read_csv(path_generated / subpath)
        df_reference = pd.read_csv(path_reference / subpath)
        pd.testing.assert_frame_equal(df_generated, df_reference)

    def compare_feather(subpath):
        df_generated = pd.read_feather(path_generated / subpath)
        df_reference = pd.read_feather(path_reference / subpath)
        pd.testing.assert_frame_equal(df_generated, df_reference)

    # compare_text("progress.log")

    # compare_csv("0/popgenstats.csv")

    compare_csv("0/visor/genotypes.csv")
    compare_csv("0/visor/phenotypes.csv")

    compare_csv("0/visor/spectra/age_at_birth.csv")
    compare_csv("0/visor/spectra/age_at_end_of_sim.csv")
    compare_csv("0/visor/spectra/age_at_genetic.csv")
    compare_csv("0/visor/spectra/age_at_overshoot.csv")
    compare_csv("0/visor/spectra/age_at_season_shift.csv")
    compare_csv("0/visor/spectra/cumulative_ages.csv")

    compare_feather("0/snapshots/demography/1000.feather")
    compare_feather("0/snapshots/genotypes/1000.feather")
    compare_feather("0/snapshots/phenotypes/1000.feather")
