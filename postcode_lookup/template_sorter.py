import abc
import datetime
from enum import Enum

from dateparser import parse
from response_builder.v1.models.base import Date, RootModel
from uk_election_timetables.calendars import Country
from uk_election_timetables.election_ids import from_election_id

# TODO: These might not be right! Implement in uk-election-timetables
#  and think about them harder
TIMETABLE_TYPES = [
    ("PRE_REGISTRATION", "Pre-registration deadline"),
    ("PRE_SOPN", "Pre-candidates nominated"),
    ("POLLING_DAY", "Polling Day"),
]


class ResponseTypes(Enum):
    NO_UPCOMING = "No upcoming elections"
    ONE_CURRENT_DATE = "Elections one date"
    MULTIPLE_DATES = "Elections more than one date"
    CONTACT_DETAILS = "Just show contact details"


class ApiModes(Enum):
    UPCOMING_ELECTIONS = "Upcoming elections"
    CONTACT_DETAILS = "Contact details"


country_map = {
    "England": Country.ENGLAND,
    "Scotland": Country.SCOTLAND,
    "Wales": Country.WALES,
    "Northern Ireland": Country.NORTHERN_IRELAND,
}


class BaseSection(abc.ABC):
    template_name = None

    def __init__(
        self, data: Date, mode: str, current_date: datetime.date
    ) -> None:
        super().__init__()
        self.current_date = current_date
        self.mode = mode
        self.data = data

    @property
    def weight(self):
        return 0


class PollingStationSection(BaseSection):
    template_name = "polling_station.html"

    @property
    def weight(self):
        poll_date = parse(self.data.date).date()
        if poll_date < self.current_date:
            return 1000

        days_before_poll = 3

        if (
            poll_date - datetime.timedelta(days=days_before_poll)
        ) < self.current_date:
            return -1000
        return 0


class ElectionDateTemplateSorter:
    def __init__(
        self,
        date_data: Date,
        country: Country,
        current_date: datetime.date = None,
    ) -> None:
        if not current_date:
            current_date = datetime.date.today()
        self.current_date = current_date

        self.date_data = date_data

        self.timetable = from_election_id(
            self.date_data.ballots[0].election_id, country=country
        )

        self.current_mode = None
        for event in self.timetable.timetable:
            print(event)
            if event["date"] <= current_date:
                self.current_mode = event["label"]
        self.sections = {
            "polling_stations": PollingStationSection(
                data=self.date_data,
                mode=self.current_mode,
                current_date=self.current_date,
            )
        }
        for section_name, section in self.sections.items():
            print(section_name, section.weight)


class TemplateSorter:
    """
    Given an API response, sorts template fragments ready for rendering

    """

    dates = []

    def __init__(
        self,
        api_response: RootModel,
        mode=ApiModes.UPCOMING_ELECTIONS,
        current_date: datetime.date = None,
    ) -> None:
        self.current_date = current_date
        self.mode = mode
        self.api_response = api_response
        for date in self.api_response.dates:
            country = country_map[self.api_response.electoral_services.nation]
            self.dates.append(
                ElectionDateTemplateSorter(
                    date, country, current_date=self.current_date
                )
            )

    @property
    def response_type(self):
        if self.mode == ApiModes.CONTACT_DETAILS:
            return ResponseTypes.CONTACT_DETAILS
        if not self.api_response.dates:
            return ResponseTypes.NO_UPCOMING
        if len(self.api_response.dates) == 1:
            return ResponseTypes.ONE_CURRENT_DATE
        return ResponseTypes.MULTIPLE_DATES

    @property
    def main_template_name(self):
        if self.response_type == ResponseTypes.CONTACT_DETAILS:
            return "results_contact_details.html"
        if self.response_type == ResponseTypes.NO_UPCOMING:
            return "results_no_upcoming.html"
        if self.response_type == ResponseTypes.ONE_CURRENT_DATE:
            return "results_one_current.html"
        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            return "results_multiple_dates.html"
        return None
