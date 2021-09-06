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

testrun:
	python3 setup.py bdist_wheel sdist
	python3 -m pip install -e .
	python3 -m aegis tests/run/test_run.yml

generate:
	. .venv/bin/activate
	python3 tests/generate.py

test:
	pytest tests/ --log-cli-level=DEBUG

manifest:
	python3 -m pip install check-manifest
	check-manifest --create

packaging_installation: 
	python3 -m pip install twine wheel

package:
	python3 -m pip install twine wheel
	rm -rf dist/*
	python3 setup.py sdist bdist_wheel
	twine check dist/*

uploadtest:
	twine upload --repository testpypi dist/*

uploadreal:
	twine upload dist/*

testinstall:
	deactivate
	rm -rf temp/venv
	python3 -m venv temp/venv
	. temp/venv/bin/activate
	python3 -m pip install --upgrade pip
	python3 -m pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple aging-of-evolving-genomes

profile:
	python3 profiling/profiler.py