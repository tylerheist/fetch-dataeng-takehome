format: 
	poetry run black .
	poetry run isort --profile black .

flake: 
	poetry run flake8 .

pytest:
	poetry run pytest .

test: format flake pytest 

run: 
	poetry run python fetchrewards_takehome/app.py
