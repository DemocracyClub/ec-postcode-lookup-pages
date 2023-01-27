import hashlib
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

TEMPLATES = {
    "base.html": {
        "source_url": "https://www.electoralcommission.org.uk/i-am-a/voter/elections-your-area/elections-your-area-feedback"
    },
    "base_cy.html": {
        "source_url": "https://www.electoralcommission.org.uk/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad/etholiadau-yn-eich-ardal-chi-adborth"
    },
}


def rewrite_urls(soup, source_url):
    tags = (
        ("link", "href"),
        ("script", "src"),
    )

    for tag, attr in tags:
        for found_tag in soup.find_all(tag):
            if attr in found_tag.attrs:
                url = found_tag[attr]
                if url.startswith("/"):
                    url = urljoin("https://www.electoralcommission.org.uk", url)
                    found_tag[attr] = url

    for a in soup.find_all("a"):

        if source_url in a["href"]:
            a["href"] = a["href"].replace(
                source_url,
                "https://www.electoralcommission.org.uk{{request.path}}",
            )
    return soup


def rewrite_asset_urls(soup, assets, static_path):
    # CSS
    for asset_type, hashed_name in assets["css"].items():
        link = soup.new_tag("link")
        link["media"] = asset_type
        link["href"] = f"/static/css/{hashed_name}"
        link["rel"] = "stylesheet"
        soup.head.append(link)

    # JS
    script = soup.new_tag("script")
    script["src"] = f"/static/js/{assets['js']['scripts']}"
    soup.body.append(script)

    return soup


def _replace_content(el, content):
    for child in el.children:
        child.replaceWith("")
    el.insert(
        0,
        BeautifulSoup(
            content,
            "html.parser",
        ),
    )


def remove_unwanted_content(soup: BeautifulSoup):
    soup.select_one("#block-locationselector").replaceWith("")

    _replace_content(
        soup.select_one(".l-main-content"),
        """
        <div class="region region-content">
            {% block content %}{% endblock content %}
        </div>
        """,
    )

    _replace_content(
        soup.select_one(".c-hero__title"),
        "{% block page_title %}{% endblock page_title %}",
    )

    _replace_content(
        soup.select_one(".c-translate-block__items"),
        "{% block language_picker %}{% endblock language_picker %}",
    )

    return soup


def add_local_font_css(soup):
    head = soup.select_one("head")
    head.insert(
        len(head.contents),
        BeautifulSoup(
            """
            {% if request.url.netloc != "www.electoralcommission.org.uk" %}
            <style>
            @font-face{
    font-family:"Swis721LtBTW05-Medium";
    font-style:normal;
    font-weight:normal;
    src:url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721MdBTW05-Medium.woff2") format("woff2"),url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721MdBTW05-Medium.woff") format("woff")
}
@font-face{
    font-family:"Swis721LtBTW05-Medium";
    font-style:italic;
    font-weight:normal;
    src:url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721MdBTW05-MediumItalic.woff2") format("woff2"),url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721MdBTW05-MediumItalic.woff") format("woff")
}
@font-face{
    font-family:"Swis721LtBTW05-Medium";
    font-style:normal;
    font-weight:bold;
    src:url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721BTWGL4W05-Bold.woff2") format("woff2"),url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721BTWGL4W05-Bold.woff") format("woff")
}
@font-face{
    font-family:"Swis721MdBTW05-Bold";
    font-style:normal;
    font-weight:normal;
    src:url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721BTWGL4W05-Bold.woff2") format("woff2"),url("/themes/custom/electoralcommission/dist/css/../fonts/swis721/Swis721BTWGL4W05-Bold.woff") format("woff")
}
            </style>
            {% endif %}
            """,
            "html.parser",
        ),
    )
    return soup


def rewrite_css_urls(asset_text, souce_url):
    urls = re.findall("url\(([^\)]+)\)", asset_text)
    for url in urls:
        cleaned_url = re.sub('"', "", url)
        if cleaned_url[0] in ["/", ".."]:
            absolute_url = urljoin(souce_url, cleaned_url)
            asset_text = asset_text.replace(cleaned_url, absolute_url)
    return asset_text


def download_assets(soup, static_path, souce_url):
    # CSS
    assets = {
        "css": {},
        "js": {"scripts": []},
    }
    for link in soup.find_all("link", {"rel": "stylesheet"}):
        if not link["href"].startswith("/"):
            continue
        if link["media"] not in assets["css"]:
            assets["css"][link["media"]] = []
        assets["css"][link["media"]].append(link["href"])
        link.decompose()

    for script in soup.find_all("script"):
        if not script.attrs.get("src"):
            continue
        if not script["src"].startswith("/"):
            continue
        assets["js"]["scripts"].append(script["src"])
        script.decompose()

    for file_type, file_data in assets.items():
        type_dir = static_path / file_type
        for file_name, files in file_data.items():
            path = type_dir / f"{file_name}.{file_type}"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                for file in files:
                    url = urljoin(souce_url, file)
                    asset_text = httpx.get(url).text
                    if file_type == "css":
                        asset_text = rewrite_css_urls(asset_text, souce_url)
                    f.write(asset_text)
                f.write(""".c-social .o-external-link::after {display: none}""")
            with open(path, "r") as final_file:
                hash = md5 = hashlib.md5(
                    final_file.read().encode("utf8")
                ).hexdigest()
                initial_name, ext = path.name.split(".")
                hashed_name = f"{initial_name}.{hash}.{ext}"
                hashed_path = path.parent / hashed_name
                with open(hashed_path, "w") as f:
                    final_file.seek(0)
                    f.write(final_file.read())
                assets[file_type][file_name] = hashed_name
    return assets


project_path = Path() / "postcode_lookup"
static_path = project_path / "static"
shutil.rmtree(static_path.absolute(), ignore_errors=True)

for template, config in TEMPLATES.items():
    template_path = project_path / "templates" / template
    req = httpx.get(config["source_url"])
    soup = BeautifulSoup(req.text, "html.parser")

    assets = download_assets(soup, static_path, config["source_url"])
    soup = rewrite_urls(soup, config["source_url"])
    soup = rewrite_asset_urls(soup, assets, static_path)
    soup = remove_unwanted_content(soup)
    soup = add_local_font_css(soup)

    with template_path.open("w") as f:
        f.write(soup.prettify())
