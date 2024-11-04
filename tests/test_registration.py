import datetime

from freezegun import freeze_time
from mock_responses import (
    CITY_OF_LONDON_COUNCIL_AND_PARL_DIFFERENT_DAYS,
    CITY_OF_LONDON_COUNCIL_AND_PARL_SAME_DAY,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
)
from template_sorter import (
    CityOfLondonRegistrationDateSection,
    RegistrationDateSection,
)


def _sections_of_type(sections, type_):
    return [s for s in sections if type(s) == type_]


@freeze_time("2024-04-16")
def test_single_ballot_not_city_of_london(
    template_sorter, election_date_template_sorter
):
    single_ballot_sorter_before_deadline = template_sorter(
        SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
        date=datetime.date(2024, 3, 16),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    sections = single_election_date_template_sorter.sections
    assert len(_sections_of_type(sections, RegistrationDateSection)) == 1
    assert (
        len(_sections_of_type(sections, CityOfLondonRegistrationDateSection))
        == 0
    )


@freeze_time("2024-04-16")
def test_city_of_london_and_parl_different_days(
    template_sorter, election_date_template_sorter
):
    single_ballot_sorter_before_deadline = template_sorter(
        CITY_OF_LONDON_COUNCIL_AND_PARL_DIFFERENT_DAYS,
        date=datetime.date(2024, 3, 16),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    sections = single_election_date_template_sorter.sections
    assert len(_sections_of_type(sections, RegistrationDateSection)) == 0
    assert (
        len(_sections_of_type(sections, CityOfLondonRegistrationDateSection))
        == 1
    )
    # ignore the parl ballot in this test


@freeze_time("2024-04-16")
def test_city_of_london_and_parl_same_day(
    template_sorter, election_date_template_sorter
):
    single_ballot_sorter_before_deadline = template_sorter(
        CITY_OF_LONDON_COUNCIL_AND_PARL_SAME_DAY,
        date=datetime.date(2024, 3, 16),
    )
    single_election_date_template_sorter = election_date_template_sorter(
        single_ballot_sorter_before_deadline,
        single_ballot_sorter_before_deadline.dates[0],
    )
    sections = single_election_date_template_sorter.sections
    assert len(_sections_of_type(sections, RegistrationDateSection)) == 1
    assert (
        len(_sections_of_type(sections, CityOfLondonRegistrationDateSection))
        == 1
    )
