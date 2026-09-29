from types import SimpleNamespace

from related_content import get_page_metadata, get_related_content
from utils import Country


def make_ballot(ballot_paper_id):
    return SimpleNamespace(ballot_paper_id=ballot_paper_id)


def make_date(*ballot_paper_ids):
    return SimpleNamespace(ballots=[make_ballot(b) for b in ballot_paper_ids])


def test_get_page_metadata_en():
    page = get_page_metadata("/voting-and-elections", language="en")
    assert page["url"] == "/voting-and-elections"


def test_get_page_metadata_cy():
    page = get_page_metadata("/voting-and-elections", language="cy")
    assert page["url"] == "/cy/pleidleisio-ac-etholiadau"


def test_get_page_metadata_with_country():
    page = get_page_metadata(
        "/voting-and-elections", language="en", country=Country.NORTHERN_IRELAND
    )
    assert page["url"] == "/voting-and-elections#NIR"


def test_get_related_content_two_links_always_present():
    assert (
        len(get_related_content([], language="en", country=Country.ENGLAND))
        == 2
    )
    assert (
        len(get_related_content([], language="cy", country=Country.ENGLAND))
        == 2
    )


def test_get_related_content_mayor_london_returns_gla_content():
    dates = [make_date("mayor.london.2026-05-07")]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    titles = [r["title"] for r in result]
    assert "Mayor of London and London Assembly" in titles
    assert "Voting in mayoral elections" not in titles


def test_get_related_content_mayor_elsewhere_returns_mayoral_content():
    dates = [make_date("mayor.tower-hamlets.2026-05-07")]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    titles = [r["title"] for r in result]
    assert "Voting in mayoral elections" in titles
    assert "Mayor of London and London Assembly" not in titles


def test_get_related_content_parl_by_election():
    dates = [make_date("parl.sheffield-central.by.2026-05-07")]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    titles = [r["title"] for r in result]
    assert "UK parliamentary by-elections" in titles
    assert "UK Parliament" not in titles


def test_get_related_content_local_by_election():
    dates = [make_date("local.tower-hamlets.by.2026-05-07")]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    titles = [r["title"] for r in result]
    assert "Local council by-elections" in titles
    assert "Local councils" not in titles


def test_get_related_content_unknown_election_type_does_not_raise():
    dates = [make_date("ref.some-area.2026-05-07")]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    # only the 2 default links
    assert len(result) == 2


def test_get_related_content_never_more_than_4_items():
    dates = [
        make_date(
            "parl.stratford-and-bow.by.2026-05-07",
            "mayor.tower-hamlets.2026-05-07",
            "gla.c.city-and-east.2026-05-07",
            "gla.a.2026-05-07",
            "local.tower-hamlets.bow-east.2026-05-07",
        )
    ]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    assert len(result) == 4


def test_get_related_content_duplicate_ballot_type_not_added_twice():
    """
    Multiple ballots of the same election type should only produce
    one related content link, not a duplicate.
    """
    dates = [
        make_date(
            "gla.c.city-and-east.2026-05-07",
            "gla.a.2026-05-07",
        )
    ]
    result = get_related_content(dates, language="en", country=Country.ENGLAND)
    titles = [r["title"] for r in result]
    assert titles.count("Mayor of London and London Assembly") == 1
    assert len(result) == 3  # 1 election-specific + 2 default
