.PHONY: clean
clean:
	rm -rf env env_ok

env_ok: requirements.txt
	rm -rf env env_ok
	python3 -m venv env
	env/bin/pip install -r requirements.txt
	touch env_ok

.PHONY: fmt
fmt: env_ok
	env/bin/isort --sp .isort.cfg src/ tests/
	env/bin/black src/ tests/

.PHONY: check
check: env_ok
	env/bin/python -m mypy \
		--no-implicit-optional \
		--check-untyped-defs \
		--ignore-missing-imports \
		./
	env/bin/python -m flake8 --select F ./ --exclude=./env
	env/bin/isort  --sp .isort.cfg  --check src/ tests/
	env/bin/black --check src/ tests/

.PHONY: test
test: check
	PYTHONPATH=./src env/bin/python -m unittest discover tests/ -p "*.py" -v