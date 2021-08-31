"""
This script is executed when you run `python3 -m aegis {path/to/config_file}`.
"""

from aegis.ecosystem import Ecosystem
from aegis.panconfiguration import pan

# TODO add typing


def main(custom_config_path=None):

    # Initialize pan
    pan.init(custom_config_path)

    # Create ecosystems
    ecosystems = [Ecosystem(i) for i in range(len(pan.params_list))]

    # Run simulation
    while pan.cycle():
        for ecosystem in ecosystems:
            ecosystem.cycle()


if __name__ == "__main__":
    main()
