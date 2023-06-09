prep:
	poetry run black .
	poetry run flake8 .
	poetry run pylint -E --rcfile=./.pylintrc app/ main.py

unittest:
	poetry run pytest -m "not end_to_end"

e2etest:
	poetry run pytest -m "end_to_end"

coverage:
	poetry run coverage run --source=main.py --source=app -m pytest -m "not end_to_end"
	poetry run coverage report
