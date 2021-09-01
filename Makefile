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
	python3 -m pip install pytest
	pytest tests/ --log-cli-level=DEBUG

manifest:
	check-manifest --create


packaging:
	python3 -m pip install wheel
	python3 setup.py sdist bdist_wheel
	twine check dist/*

uploadtest:
	python3 -m pip install twine
	twine upload --repository testpypi dist/*

uploadreal:
	twine upload dist/*