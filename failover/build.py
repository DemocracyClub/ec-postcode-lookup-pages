from pathlib import Path

from jinja2 import ChainableUndefined, Environment, FileSystemLoader
from starlette.requests import Request

from postcode_lookup.related_content import get_page_metadata

templates_root = (
    Path(__file__).parent.parent.absolute() / "postcode_lookup" / "templates"
)
failover_templates_dir = Path(__file__).parent.absolute()


class _StubRequest(Request):
    """A real Request over a minimal scope, so templates expecting
    request.scope fields (current_language, base_template, url, etc.)
    behave the same as they do for a real request."""

    def __init__(self):
        super().__init__(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "query_string": b"",
                "headers": [],
                "root_path": "",
                "scheme": "https",
                "server": ("www.electoralcommission.org.uk", 443),
                "client": None,
                "current_language": "en",
                "base_template": "base.html",
            }
        )


env = Environment(
    loader=FileSystemLoader([failover_templates_dir, templates_root]),
    undefined=ChainableUndefined,
    extensions=["jinja2.ext.i18n"],
)
env.globals["get_page_metadata"] = get_page_metadata
env.globals["request"] = _StubRequest()
env.install_null_translations()

out_file = Path("failover/dist/index.html")
out_file.parent.mkdir(exist_ok=True)

out_file.write_text("")
with out_file.open("a") as out:
    for chunk in env.get_template("failover.html").generate():
        out.write(chunk)
