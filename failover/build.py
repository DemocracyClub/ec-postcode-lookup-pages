from pathlib import Path

from jinja2 import ChainableUndefined, Environment, FileSystemLoader

templates_root = (
    Path(__file__).parent.parent.absolute() / "postcode_lookup" / "templates"
)
failover_templates_dir = Path(__file__).parent.absolute()


env = Environment(
    loader=FileSystemLoader([failover_templates_dir, templates_root]),
    undefined=ChainableUndefined,
)

out_file = Path("failover/dist/index.html")
out_file.parent.mkdir(exist_ok=True)

out_file.write_text("")
with out_file.open("a") as out:
    for chunk in env.get_template("failover.html").generate():
        out.write(chunk)
