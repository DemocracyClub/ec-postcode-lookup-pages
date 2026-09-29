# Installation

Requires:
- Python >= 3.12
- [`uv==0.11.*`](https://github.com/astral-sh/uv) installed globally.

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

# Updating pages mirror

We mirror the page titles and descriptions (in English and Welsh)
for a bunch of pages on the EC site to make it easy to link out to
content elsewhere on the site.

If we need to update this, run

```shell
uv run lib/pages_mirror/harvest.py
```

This will output `postcode_lookup/data/pages.json`.

# Linking to pages on electoralcommission.org.uk

When we to link to content elsewhere on electoralcommission.org.uk there are two things we want to ensure:

1. If the user is viewing the current page in English, we want to link them to English language content elsewhere on the site. If the user is viewing the current page in Welsh, we want to link them to Welsh language content elsewhere on the site.

2. Many pages on electoralcommission.org.uk have country-specific information. For example, https://www.electoralcommission.org.uk/voting-and-elections/voter-id#WLS has different information on it to https://www.electoralcommission.org.uk/voting-and-elections/voter-id#NIR . If we already know what country the user is in, we want to link them to the right content.

When we link to content elsewhere on electoralcommission.org.uk ensure we have a copy of the page and metadata in the mirror and then use the `get_page_metadata()` helper to link to it.

✔ Good

```jinja
{# using the pre-translated title and description #}
{% with page = get_page_metadata(
  "/voting-and-elections/voter-id",
  request.scope.current_language)
%}
  <a href="{{ page.url }}">
    <h3>{{ page.title }}</h3>
  </a>
  <p>{{ page.description }}</p>
{% endwith %}
```

```jinja
{# using the URL only #}
{% with page = get_page_metadata(
  "/voting-and-elections/voter-id",
  request.scope.current_language,
  country)
%}
  {% trans url=page.url %}
    Find out more about
    <a href="{{ url }}">ID requirements</a>
  {% endtrans %}
{% endwith %}
```

✖ Bad

```jinja
{# not appropriately translated or localised #}
{% trans %}
  Find out more about
  <a href="/voting-and-elections/voter-id">ID requirements</a>
{% endtrans %}
```
