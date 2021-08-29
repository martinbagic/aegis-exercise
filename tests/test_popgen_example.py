# `python3 -m pytest tests/test_popgen_example.py --log-cli-level=DEBUG`

import pytest

from aegis.classes import popgenstats


@pytest.mark.parametrize(
    "pop_size_history,expected",
    [
        ([100, 200, 300, 400], 192.0),
        ([100, 100, 100, 100], 100.0),
        ([100], 100.0),
        ([10000], 10000.0),
        ([1, 1000], 1.998),
    ],
)
def test_get_Ne(pop_size_history, expected):
    Ne = popgenstats.get_Ne(pop_size_history)
    assert pytest.approx(Ne, 0.001) == expected
