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

testnew: generate test

generate:
	. .venv/bin/activate
	python3 tests/generate.py

test:
	pytest tests/ --log-cli-level=DEBUG

manifest:
	check-manifest --create