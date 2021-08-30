# `python3 -m pytest tests/test_popgen_get_Ne.py --log-cli-level=DEBUG`

import pytest
import numpy as np

from aegis.classes import popgenstats


@pytest.mark.parametrize(
    "get_Ne_valid_input,expected",
    [
        ([100], 100.0),
        ([100, 200, 300, 400], 192.0),
        (np.array([100]), 100.0),
        (np.array([100, 200, 300, 400]), 192.0)
    ],
)
def test_get_Ne_valid_input(get_Ne_valid_input, expected):
    Ne = popgenstats.get_Ne(get_Ne_valid_input)
    assert pytest.approx(Ne, 0.0001) == expected
