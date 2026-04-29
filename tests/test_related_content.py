from types import SimpleNamespace

from related_content import get_related_content


def make_ballot(ballot_paper_id):
    return SimpleNamespace(ballot_paper_id=ballot_paper_id)


def make_date(*ballot_paper_ids):
    return SimpleNamespace(ballots=[make_ballot(b) for b in ballot_paper_ids])


def test_two_links_always_present():
    assert len(get_related_content([], language="en")) == 2
    assert len(get_related_content([], language="cy")) == 2


def test_mayor_london_returns_gla_content():
    dates = [make_date("mayor.london.2026-05-07")]
    result = get_related_content(dates, language="en")
    titles = [title for title, _ in result]
    assert "Mayor of London and London Assembly" in titles
    assert "Mayoral elections" not in titles


def test_mayor_elsewhere_returns_mayoral_content():
    dates = [make_date("mayor.tower-hamlets.2026-05-07")]
    result = get_related_content(dates, language="en")
    titles = [title for title, _ in result]
    assert "Mayoral elections" in titles
    assert "Mayor of London and London Assembly" not in titles


def test_parl_by_election():
    dates = [make_date("parl.sheffield-central.by.2026-05-07")]
    result = get_related_content(dates, language="en")
    titles = [title for title, _ in result]
    assert "UK parliamentary by-elections" in titles
    assert "UK Parliament" not in titles


def test_local_by_election():
    dates = [make_date("local.tower-hamlets.by.2026-05-07")]
    result = get_related_content(dates, language="en")
    titles = [title for title, _ in result]
    assert "Local council by-elections" in titles
    assert "Local councils" not in titles


def test_unknown_election_type_does_not_raise():
    dates = [make_date("ref.some-area.2026-05-07")]
    result = get_related_content(dates, language="en")
    # only the 2 always-shown links
    assert len(result) == 2


def test_never_more_than_4_items_inner_break():
    """
    Single date with many ballots of different types exercises the inner
    (ballot-level) break: once 2 election-specific links are collected,
    remaining ballots on the same date are skipped.
    """
    dates = [
        make_date(
            "parl.stratford-and-bow.by.2026-05-07",
            "mayor.tower-hamlets.2026-05-07",
            "gla.c.city-and-east.2026-05-07",
            "gla.a.2026-05-07",
            "local.tower-hamlets.bow-east.2026-05-07",
        )
    ]
    result = get_related_content(dates, language="en")
    assert len(result) == 4


def test_never_more_than_4_items_outer_break():
    """
    Multiple dates, each with a single ballot, exercises the outer
    (date-level) break: once 2 election-specific links are collected
    across dates, remaining dates are skipped.
    """
    dates = [
        make_date("parl.stratford-and-bow.by.2026-05-07"),
        make_date("mayor.tower-hamlets.2026-05-08"),
        make_date("gla.c.city-and-east.2026-05-09", "gla.a.2026-05-07"),
        make_date("local.tower-hamlets.bow-east.2026-05-10"),
    ]
    result = get_related_content(dates, language="en")
    assert len(result) == 4


def test_duplicate_ballot_type_not_added_twice():
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
    result = get_related_content(dates, language="en")
    titles = [title for title, _ in result]
    assert titles.count("Mayor of London and London Assembly") == 1
    assert len(result) == 3  # 1 election-specific + 2 always-shown
