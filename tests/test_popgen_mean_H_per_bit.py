# `python3 -m pytest tests/test_popgen_mean_h_per_bit.py --log-cli-level=DEBUG`

import pytest
import numpy as np

from aegis.classes import popgenstats


example1 = np.array(
    [
        [
            [0, 1, 1, 0, 1, 1],
            [0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 0],
            [1, 0, 1, 1, 0, 1],
        ],
        [
            [1, 1, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0],
        ],
        [
            [0, 1, 1, 0, 1, 1],
            [0, 0, 0, 1, 0, 1],
            [1, 1, 0, 1, 1, 0],
            [1, 0, 1, 1, 0, 1],
        ],
        [
            [1, 0, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 0],
        ],
        [
            [0, 1, 1, 0, 1, 1],
            [0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 0, 1, 1, 0, 1],
        ],
        [
            [1, 1, 0, 0, 1, 0],
            [1, 0, 1, 1, 1, 1],
            [0, 1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 1],
        ],
        [
            [1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ],
        [
            [1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ],
    ]
)

example2 = np.array(
    [[[1, 1], [1, 1], [1, 0], [1, 0]], [[0, 1], [0, 0], [1, 1], [1, 0]]]
)

example3 = np.array(
    [
        [
            [1, 1],
            [1, 1],
        ],
        [
            [0, 0],
            [1, 0],
        ],
    ]
)

example4 = np.array(
    [
        [
            [1, 1],
        ],
        [
            [1, 1],
        ],
    ]
)

example5 = np.array(
    [
        [
            [0],
        ]
    ]
)

example6 = np.array(
    [
        [
            [1],
        ]
    ]
)


@pytest.mark.parametrize(
    "mean_h_per_bit_valid_input,expected",
    [
        (
            (example1, "asexual_diploid"),
            np.array([4, 3, 3, 3, 3, 3, 3, 6, 7, 3, 3, 6]) / 8,
        ),
        ((example2, "sexual"), np.array([1, 0, 1, 2]) / 2),
        ((example3, "asexual_diploid"), np.array([0, 1]) / 2),
        ((example4, "sexual"), np.array([0]) / 2),
        ((example5, "asexual"), np.array([])),
        ((example6, "asexual"), np.array([])),
    ],
)
def test_mean_h_per_bit_valid_input(mean_h_per_bit_valid_input, expected):
    h = popgenstats.mean_h_per_bit(*mean_h_per_bit_valid_input)
    assert pytest.approx(h, 0.0001) == expected
