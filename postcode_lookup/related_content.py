import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse

with open(Path(__file__).parent / "data" / "pages.json") as f:
    PAGES = json.load(f)


def get_page_metadata(url, language="en", country=None):
    page = PAGES[url][language]
    if country:
        parsed_url = urlparse(page["url"])
        parsed_url = parsed_url._replace(fragment=country.value)
        page["url"] = urlunparse(parsed_url)
    return page


RELATED_CONTENT = {
    "nia": "/voting-and-elections/how-elections-work/types-elections/northern-ireland-assembly",
    "senedd": "/voting-and-elections/how-elections-work/types-elections/voting-senedd-elections",
    "sp": "/voting-and-elections/how-elections-work/types-elections/scottish-parliament",
    "pcc": "/voting-and-elections/how-elections-work/types-elections/police-and-crime-commissioners",
    "mayor": "/voting-and-elections/how-elections-work/types-elections/mayoral-elections",
    "gla": "/voting-and-elections/how-elections-work/types-elections/mayor-london-and-london-assembly",
    "parl.by": "/voting-and-elections/how-elections-work/types-elections/uk-parliamentary-elections",
    "parl": "/voting-and-elections/how-elections-work/types-elections/uk-parliament",
    "local.by": "/voting-and-elections/how-elections-work/types-elections/local-council-elections",
    "local": "/voting-and-elections/how-elections-work/types-elections/local-councils",
}


def get_content_key(ballot_id):
    id_parts = ballot_id.split(".")
    election_type = id_parts[0]
    org = id_parts[1]
    by_election = id_parts[-2] == "by"

    if election_type == "mayor" and org != "london":
        return "mayor"
    if (election_type == "mayor" and org == "london") or (
        election_type == "gla"
    ):
        return "gla"
    if by_election and election_type in ("parl", "local"):
        return f"{election_type}.by"
    return election_type


def get_related_content(dates, language, country):
    related_content = []
    seen_keys = set()

    """
    Add related for election types, avoiding duplicates.

    Ballots are already sorted by date and charisma
    so we will prioritise elections that are soon/interesting
    """
    for date in dates:
        for ballot in date.ballots:
            key = get_content_key(ballot.ballot_paper_id)
            if key in RELATED_CONTENT and key not in seen_keys:
                related_content.append(
                    get_page_metadata(RELATED_CONTENT[key], language, country)
                )
                seen_keys.add(key)

    related_content.append(
        get_page_metadata(
            "/voting-and-elections/how-elections-work/types-elections", language
        )
    )
    related_content.append(get_page_metadata("/voting-and-elections", language))

    return related_content[:4]
