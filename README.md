# Installation

Requires:
- Python >= 3.12
- [`uv==0.8.*`](https://github.com/astral-sh/uv) installed globally.

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

# Updating base templates

We pull HTML, JS and CSS from donor pages on the EC site.

To update these (for example, if there's a change to the design), run:

```shell
uv run lib/template_generator/generate_base_template.py
```

This will update various front end assets in `postcode_lookup/static`.

See [lib/template_generator/README.md](lib/template_generator/README.md) for
more information about this script.
