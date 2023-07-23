test:
	python -m pytest tests --cov spoterm --cov-report term-missing

pep8:
	pycodestyle spoterm --max-line-length=120

lint:
	pylint spoterm/ --rcfile=.pylintrc

mypy:
	python -m mypy -p spoterm --ignore-missing-imports
