import subprocess

import pathlib

test_path = pathlib.Path(__file__).absolute().parent

subprocess.run("python3 -m aegis sim conf.yml -o".split(), cwd=str(test_path / "test_1"))
subprocess.run("python3 -m aegis sim conf.yml -o".split(), cwd=str(test_path / "test_2"))