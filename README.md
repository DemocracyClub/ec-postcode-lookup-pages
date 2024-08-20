# Installation

Python >= 3.12 required.

Make a new virtualenv.

```shell
$ pip install -U pip
$ pip install pipenv
$ pipenv sync --dev
$ playwright install
```

Run tests:

```shell
$ pytest
```

Run the service:

```shell
$ uvicorn postcode_lookup.app:app --reload
```

Visit `http://127.0.0.1:8000`
