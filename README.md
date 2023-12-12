![](https://img.shields.io/badge/code%20style-black-black "Code style: Black")

# Installation

Python >= 3.10 required.

Make a new virtualenv.

```shell
$ pip install -U pip
$ pip install pipenv
$ pipenv install --dev
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
