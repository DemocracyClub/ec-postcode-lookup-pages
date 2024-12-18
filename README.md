# Installation

Requires:
- Python >= 3.12
- [`uv>=0.4.27,<0.5.0`](https://github.com/astral-sh/uv) installed globally.

```shell
$ uv sync --dev
$ playwright install
```

Run tests:

```shell
$ uv run pytest
```

Run the service:

```shell
$ uv run uvicorn postcode_lookup.app:app --reload
```

Visit `http://127.0.0.1:8000`
