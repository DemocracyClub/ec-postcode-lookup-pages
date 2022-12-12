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
            a["href"] = a["href"].replace(source_url, "https://www.electoralcommission.org.uk{{request.path}}")

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
    head.insert(len(head.contents), BeautifulSoup(
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
        ))
    return soup


for template, config in TEMPLATES.items():
    req = httpx.get(config["source_url"])
    soup = BeautifulSoup(req.text, "html.parser")

    soup = rewrite_urls(soup, config["source_url"])
    soup = remove_unwanted_content(soup)
    soup = add_local_font_css(soup)

    template_path = Path() / "postcode_lookup" / "templates" / template
    with template_path.open("w") as f:
        f.write(soup.prettify())
