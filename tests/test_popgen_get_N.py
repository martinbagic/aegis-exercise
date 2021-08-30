# `python3 -m pytest tests/test_popgen_get_N.py --log-cli-level=DEBUG`

import pytest
import numpy as np

from aegis.classes import popgenstats


@pytest.mark.parametrize(
    "get_N_valid_input,expected",
    [
        ([100], 100),
        ([100, 200, 300, 400], 400),
        (np.array([100]), 100),
        (np.array([100, 200, 300, 400]), 400),
    ],
)
def test_get_N_valid_input(get_N_valid_input, expected):
    N = popgenstats.get_N(get_N_valid_input)
    assert pytest.approx(N, 0.0001) == expected
