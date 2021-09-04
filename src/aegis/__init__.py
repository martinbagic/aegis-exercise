"""
This script is executed when this package is imported.
"""


# TODO add typing


def main(custom_config_path=None):
    from aegis.ecosystem import Ecosystem
    from aegis.panconfiguration import pan

    # Initialize pan
    pan.init(custom_config_path)

    # Create ecosystems
    ecosystems = [Ecosystem(i) for i in range(len(pan.params_list))]

    # Run simulation
    while pan.run_stage():
        for ecosystem in ecosystems:
            ecosystem.run_stage()
