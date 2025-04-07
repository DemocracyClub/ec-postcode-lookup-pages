import datetime

from freezegun import freeze_time
from uk_election_timetables.election_ids import from_election_id


@freeze_time("2024-04-12")
def test_uk_election_timetable():
    """test that the election timetable is as expected"""
    election = from_election_id("parl.2024-05-02", country="England")
    assert election.timetable == [
        {
            "label": "List of candidates published",
            "date": datetime.date(2024, 4, 5),
            "event": "SOPN_PUBLISH_DATE",
        },
        {
            "label": "Register to vote deadline",
            "date": datetime.date(2024, 4, 16),
            "event": "REGISTRATION_DEADLINE",
        },
        {
            "label": "Postal vote application deadline",
            "date": datetime.date(2024, 4, 17),
            "event": "POSTAL_VOTE_APPLICATION_DEADLINE",
        },
        {
            "label": "VAC application deadline",
            "date": datetime.date(2024, 4, 24),
            "event": "VAC_APPLICATION_DEADLINE",
        },
    ]
    assert election.poll_date - election.timetable[0][
        "date"
    ] == datetime.timedelta(days=27)
    assert election.poll_date - election.timetable[1][
        "date"
    ] == datetime.timedelta(days=16)
    assert election.poll_date - election.timetable[2][
        "date"
    ] == datetime.timedelta(days=15)
    assert election.poll_date - election.timetable[3][
        "date"
    ] == datetime.timedelta(days=8)


# TODO: These aren't timetable test but should be included in the test suite
# once content is sorted to be sure the correct text appears on the page at the correct time.

# @freeze_time("2024-04-01")
# def test_day_before_election_day(
#     template_sorter, election_date_template_sorter
# ):
#     """this tests is after sopn day, but
#     before election day. test that the page shows
#     'you have an election tomorrow'
#     including any other upcoming elections, candidates,
#     and polling station if available in that order.
#     assert that registration and postal vote deadline are not shown."""


# def test_election_day(template_sorter, election_date_template_sorter):
#     """this tests is on election day. test that the page shows
#     'you have an election today' with the date and ballot title,
#     then candidates and polling station if available in that order.
#     including any other upcoming elections should be at the bottom of the page.
#     assert that registration and postal vote deadline are not shown."""

# def test_after_election_day(template_sorter, election_date_template_sorter):
#     """this tests is after election day. test that the page shows
#     no upcoming elections. test that the page only shows registration
#     information"""
