# Recipes

A recipe manager to practice Python and solve a programming exercise.

Original exercise requires a Ruby on Rails backend, but this is a Python implementation ¯\_ (ツ)_/¯. 

## Dependencies

- Python + pip
- Makefile

## How to operate

Use makefile commands to perform operations

- Set environment and install requirements:

    `make env_ok`

- Clean environment:

    `make clean`

- Format code and sort imported libraries with [black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/):

    `make fmt`

- Analize code with [mypy](https://pypi.org/project/mypy/) and [flake8](https://pypi.org/project/flake8/):

    `make check`

- Run unit tests:

    `make test`