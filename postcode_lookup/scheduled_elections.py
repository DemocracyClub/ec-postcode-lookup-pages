import datetime as dt

from starlette_babel import gettext_lazy as _
from uk_election_timetables.calendars import Country
from utils import date_format

"""
Rough calendar of known upcoming scheduled election dates
where those are easy to express at a very high level.
This won't need updating super often
but it will go stale at some point.

Note: It might be tempting to add "London" in here but
1. City of London Corporation has its own wierd schedule
2. There are a number of authorities inside London with local authority mayors:
    - Croydon
    - Hackney
    - Lewisham
    - Newham
    - Tower Hamlets
..which is enough edge cases that it is
not sensible to try and generalse about London here.
"""
KNOWN_SCHEDULED_ELECTIONS = {
    Country.SCOTLAND: [
        dt.date(2027, 5, 6),  # Local Councils
        dt.date(2031, 5, 1),  # Scottish Parliament
    ],
    Country.WALES: [
        dt.date(2027, 5, 6),  # Local Councils
        dt.date(2031, 5, 1),  # Senedd
    ],
    Country.NORTHERN_IRELAND: [
        dt.date(2027, 5, 6),  # Local Councils and NI Assembly
        dt.date(2031, 5, 1),  # Local Councils
    ],
    Country.ENGLAND: [],  # its complicated
}


def get_next_scheduled_election_date(country):
    try:
        elections = KNOWN_SCHEDULED_ELECTIONS[country]
    except KeyError:
        return None

    now = dt.date.today()
    for election_date in elections:
        if election_date > now:
            return election_date
    return None


def get_next_scheduled_election_block(country):
    date = get_next_scheduled_election_date(country)
    if country == Country.ENGLAND or not date:
        return None

    """
    Note: This is a bit clunky,
    but this is a sentence where we can't get away with

    "The next scheduled elections in {country} will take place on {date}"

    because of mutations
    "Wales" --> "Cymru"
    but
    "in Wales" --> "yng Nghymru"

    so we need a bit of duplication to allow
    translators to work with the text in context
    """
    if country == Country.SCOTLAND:
        return _(
            "The next scheduled elections in Scotland will take place on {date}"
        ).format(date=date_format(date))
    if country == Country.WALES:
        return _(
            "The next scheduled elections in Wales will take place on {date}"
        ).format(date=date_format(date))
    if country == Country.NORTHERN_IRELAND:
        return _(
            "The next scheduled elections in Northern Ireland will take place on {date}"
        ).format(date=date_format(date))

    return None


def get_next_general_election_block():
    next_ge_date = dt.date(2029, 8, 15)
    if dt.datetime.now().date() < dt.date(2029, 7, 12):
        return _(
            "The next UK General Election must be held no later than {date}, however the prime minister can choose to hold it at any point before this."
        ).format(date=date_format(next_ge_date))
    return None
