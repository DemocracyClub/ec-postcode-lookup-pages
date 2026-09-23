import json
import logging
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

import bs4
from wreq import Emulation
from wreq.blocking import Client
from wreq.redirect import Policy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

URLS = [
    "https://www.electoralcommission.org.uk/i-am-a/voter/register-vote-and-update-your-details",
    "https://www.electoralcommission.org.uk/i-am-a/voter/apply-vote-post",
    "https://www.electoralcommission.org.uk/i-am-a/voter/apply-vote-proxy",
    "https://www.electoralcommission.org.uk/i-am-a/voter/voter-id",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/northern-ireland-assembly",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/voting-senedd-elections",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/scottish-parliament",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/police-and-crime-commissioners",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/mayoral-elections",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/mayor-london-and-london-assembly",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/uk-parliamentary-elections",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/uk-parliament",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/local-council-elections",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections/local-councils",
    "https://www.electoralcommission.org.uk/voting-and-elections/how-elections-work/types-elections",
    "https://www.electoralcommission.org.uk/voting-and-elections",
]


client = Client(emulation=Emulation.Safari26)


def _get(url):
    # space out requests
    sleep(5)

    logger.info(f"Requesting {url} ...")
    return client.get(url, redirect=Policy.limited())


def extract_meta(soup: bs4.BeautifulSoup, url: str) -> dict:
    path = urlparse(url).path

    title_tag = soup.find("meta", property="og:title")
    if not title_tag:
        raise Exception(f"Failed to find og:title for {path}")

    description_tag = soup.find("meta", property="og:description")
    if not description_tag:
        description_tag = title_tag
        logger.error(
            f"Error: Failed to find og:description for {path}, using og:title instead"
        )

    return {
        "url": path,
        "title": title_tag["content"] if title_tag else None,
        "description": description_tag["content"] if description_tag else None,
    }


def harvest():
    results = {}

    for url in URLS:
        en_path = urlparse(url).path

        en_response = _get(url)
        en_response.raise_for_status()
        en_soup = bs4.BeautifulSoup(en_response.text(), "html.parser")

        cy_link = en_soup.find("link", rel="alternate", hreflang="cy")
        cy_url = cy_link["href"] if cy_link else None

        if not cy_url:
            raise Exception(f"Failed to find translated page for {en_path}")

        cy_response = _get(cy_url)
        en_response.raise_for_status()
        cy_soup = bs4.BeautifulSoup(cy_response.text(), "html.parser")

        results[en_path] = {
            "en": extract_meta(en_soup, url),
            "cy": extract_meta(cy_soup, cy_url),
        }

    outfile = (
        Path(__file__).parent
        / ".."
        / ".."
        / "postcode_lookup"
        / "data"
        / "pages.json"
    )
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Wrote {len(results)} pages to {outfile}")


if __name__ == "__main__":
    harvest()
