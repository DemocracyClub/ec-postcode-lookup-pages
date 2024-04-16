import datetime

import pytest
from freezegun import freeze_time
from mock_responses import (
    MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
    NO_LOCAL_BALLOTS,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
)
from template_sorter import (
    ApiModes,
    ElectionDateTemplateSorter,
    TemplateSorter,
)
from uk_election_timetables.calendars import Country
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


# https://election-timetable.democracyclub.org.uk/?election_date=2024-05-02


@pytest.fixture
def template_sorter():
    def get_template_sorter(mock_response, date):
        api_response = mock_response
        # The dates exist in the api_response, but not
        # in the format that matches the RootBuilder:
        # dates = api_response._values["dates"] vs
        # dates = api_response.dates so I've set it here.
        api_response.dates = api_response._values["dates"]
        mode = ApiModes.UPCOMING_ELECTIONS

        sorter = TemplateSorter(
            api_response=api_response, mode=mode, current_date=date
        )
        sorter.country = Country.ENGLAND
        sorter.dates = api_response.dates

        return sorter

    return get_template_sorter


@pytest.fixture
def election_date_template_sorter():
    def get_election_date_template_sorter(template_sorter, date):
        election_date_sorter = ElectionDateTemplateSorter(
            date_data=date,
            country=template_sorter.country,
            current_date=template_sorter.current_date,
            response_type=template_sorter.response_type,
        )
        election_date_sorter.current_date = template_sorter.current_date

        election_date_sorter.timetable = from_election_id(
            template_sorter.dates[0].ballots[0].election_id,
            country=template_sorter.country,
        )

        return election_date_sorter

    return get_election_date_template_sorter


@freeze_time("2024-04-04")
def test_sopn_day(template_sorter, election_date_template_sorter):
    """this tests is after postal vote deadline, but
    before sopn day. test that the page shows the upcoming elections
    and polling station if available at the top of the page
    assert that registration and postal vote deadline and candidates are not shown.
    """
    # before deadline
    single_ballot_sorter_before_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 4),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    # PollingStationSection
    assert single_election_date_template_sorter.sections[0].weight == 1000
    # This is the first event deadline in the sequence so there is nothing that
    # appears in the timetable before it.
    assert single_election_date_template_sorter.sections[0].mode is None
    # BallotSection
    assert single_election_date_template_sorter.sections[1].weight == 6000
    assert single_election_date_template_sorter.sections[1].mode is None

    multiple_ballot_template_sorter_before_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 4),
    )
    # although this is 'first' in the list, it's the second event in the sequence,
    # so the date is later in the timetable.
    first_election_date = multiple_ballot_template_sorter_before_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "List of candidates published"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "List of candidates published"
    )

    # after deadline
    single_ballot_sorter_after_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 7),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_after_deadline,
        single_ballot_sorter_after_deadline.dates[0],
    )
    # TODO: I would have expected the mode to change here after
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert single_election_date_template_sorter.sections[0].mode is None
    assert single_election_date_template_sorter.sections[1].weight == 6000
    assert single_election_date_template_sorter.sections[1].mode is None

    multiple_ballot_template_sorter_after_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 6),
    )
    first_election_date = multiple_ballot_template_sorter_after_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = multiple_ballot_template_sorter_after_deadline.dates[
        1
    ]
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "List of candidates published"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "List of candidates published"
    )

    with pytest.raises(Exception):
        template_sorter(NO_LOCAL_BALLOTS, date=datetime.date(2024, 4, 6))


@freeze_time("2024-04-16")
def test_registration_deadline(template_sorter, election_date_template_sorter):
    """test that the page shows the voter registration deadline
    and advice on how to register at the top of the page.
    assert that candidates are not shown. this test will use the
    default settings of the template_sorter fixture"""

    single_ballot_sorter_before_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 16),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    assert len(single_election_date_template_sorter.sections) == 3
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "Register to vote deadline"
    )
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "Register to vote deadline"
    )

    multiple_ballot_template_sorter_before_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 16),
    )

    first_election_date = multiple_ballot_template_sorter_before_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "Register to vote deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "Register to vote deadline"
    )

    # this is after the registration deadline so the weight
    single_ballot_sorter_after_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 17),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_after_deadline,
        single_ballot_sorter_after_deadline.dates[0],
    )
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    multiple_ballot_template_sorter_after_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 17),
    )
    first_election_date = multiple_ballot_template_sorter_after_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = multiple_ballot_template_sorter_after_deadline.dates[
        1
    ]
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    with pytest.raises(Exception):
        template_sorter(NO_LOCAL_BALLOTS, date=datetime.date(2024, 4, 17))


@freeze_time("2024-04-17")
def test_postal_vote_application_deadline(
    template_sorter, election_date_template_sorter
):
    """test that the page shows the postal vote deadline
    and advice on how to vote by post at the top of the page.
    assert that registration deadline and candidates are not shown."""
    # assert that the template_sorter returns the correct includes
    # and the correct weight for the postal vote deadline
    single_ballot_sorter_before_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 16),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    # PollingStationSection
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "Register to vote deadline"
    )
    # BallotSection
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "Register to vote deadline"
    )

    multiple_ballot_template_sorter_before_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 16),
    )
    first_election_date = multiple_ballot_template_sorter_before_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "Register to vote deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "Register to vote deadline"
    )

    single_ballot_sorter_after_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 18),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_after_deadline,
        single_ballot_sorter_after_deadline.dates[0],
    )
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    multiple_ballot_template_sorter_after_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 18),
    )
    first_election_date = multiple_ballot_template_sorter_after_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    with pytest.raises(Exception):
        template_sorter(NO_LOCAL_BALLOTS, date=datetime.date(2024, 4, 18))


@freeze_time("2024-04-23")
def test_vac_application_deadline(
    template_sorter, election_date_template_sorter
):
    """this tests is after vac application deadline.
    test that the page shows the vac application advice at the
    top of the page and upcoming elections
    and polling station if available next.
    assert that registration and postal vote deadline and
    candidates are not shown.
    """
    single_ballot_sorter_before_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 23),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    # PollingStationSection
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    # BallotSection
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    multiple_ballot_template_sorter_before_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 23),
    )
    first_election_date = multiple_ballot_template_sorter_before_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_before_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "Postal vote application deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "Postal vote application deadline"
    )

    single_ballot_sorter_after_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 4, 25),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_after_deadline,
        single_ballot_sorter_after_deadline.dates[0],
    )
    assert single_election_date_template_sorter.sections[0].weight == 1000
    assert (
        single_election_date_template_sorter.sections[0].mode
        == "VAC application deadline"
    )
    assert single_election_date_template_sorter.sections[1].weight == 1001
    assert (
        single_election_date_template_sorter.sections[1].mode
        == "VAC application deadline"
    )

    multiple_ballot_template_sorter_after_deadline = template_sorter(
        MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
        date=datetime.date(2024, 4, 25),
    )
    first_election_date = multiple_ballot_template_sorter_before_deadline.dates[
        0
    ]
    first_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, first_election_date
    )
    assert len(first_election_date_template_sorter.sections) == 3
    assert first_election_date_template_sorter.sections[0].weight == 1000
    assert first_election_date_template_sorter.sections[0].mode is None
    assert first_election_date_template_sorter.sections[1].weight == 6000
    assert first_election_date_template_sorter.sections[1].mode is None

    second_election_date = (
        multiple_ballot_template_sorter_before_deadline.dates[1]
    )
    second_election_date_template_sorter = election_date_template_sorter(
        multiple_ballot_template_sorter_after_deadline, second_election_date
    )
    assert len(second_election_date_template_sorter.sections) == 3
    assert second_election_date_template_sorter.sections[0].weight == 1000
    assert (
        second_election_date_template_sorter.sections[0].mode
        == "VAC application deadline"
    )
    assert second_election_date_template_sorter.sections[1].weight == 1001
    assert (
        second_election_date_template_sorter.sections[1].mode
        == "VAC application deadline"
    )

    with pytest.raises(Exception):
        template_sorter(NO_LOCAL_BALLOTS, date=datetime.date(2024, 4, 25))


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
