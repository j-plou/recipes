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
	env/bin/isort --sp .isort.cfg app/*.py
	env/bin/black app/*.py

.PHONY: check
check: env_ok
	env/bin/python -m mypy \
		--no-implicit-optional \
		--check-untyped-defs \
		--ignore-missing-imports \
		./
	env/bin/python -m flake8 --select F ./ --exclude=./env
	env/bin/isort  --sp .isort.cfg  --check app/*.py
	env/bin/black --check app/*.py

.PHONY: test
test: check
	env/bin/python -m unittest discover ./app -p "*.py" -v