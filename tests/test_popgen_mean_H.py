# `python3 -m pytest tests/test_popgen_mean_H.py --log-cli-level=DEBUG`

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
    "mean_H_valid_input,expected",
    [
        (
            (example1, "asexual_diploid"),
            np.mean(np.array([7, 6, 8, 7, 6, 7, 3, 3]) / 12),
        ),
        ((example2, "sexual"), 0.5),
        ((example3, "asexual_diploid"), 0.25),
        ((example4, "sexual"), 0),
        ((example5, "asexual"), np.array([])),
        ((example6, "asexual"), np.array([])),
    ],
)
def test_mean_H_valid_input(mean_H_valid_input, expected):
    H = popgenstats.mean_H(*mean_H_valid_input)
    assert pytest.approx(H, 0.0001) == expected