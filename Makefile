install:
	python -m pip install --upgrade pip setuptools wheel &&\
	python -m pip install -r requirements.txt

test:
	python -m pytest -vv --cov --cov-report=term-missing

coverage:
	coverage report --fail-under=90

format:
	python -m black **/*.py

lint:
	python -m pylint --disable=R,C **/*.py --fail-under=9.5

all: install lint test format