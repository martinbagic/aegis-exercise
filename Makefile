.ONESHELL:

all: venv test

venv:
	echo "\n***\n"
	rm -rf .venv
	python3 -m venv .venv
	. .venv/bin/activate
	python3 -m pip install wheel
	python3 setup.py bdist_wheel sdist
	python3 -m pip install -e .

test:
	echo "\n***\n"
	. .venv/bin/activate
	python3 -m pytest tests/ --log-cli-level=DEBUG

manifest:
	check-manifest --create