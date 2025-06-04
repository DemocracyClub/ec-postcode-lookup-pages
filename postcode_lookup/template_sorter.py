import abc
import datetime
from enum import Enum
from functools import cached_property
from typing import Dict, List, Optional

from dateparser import parse
from postal_votes import get_postal_vote_dispatch_dates
from response_builder.v1.models.base import Date, RootModel
from starlette_babel import gettext_lazy as _
from uk_election_timetables.calendars import Country
from uk_election_timetables.election import TimetableEvent
from uk_election_timetables.election_ids import from_election_id
from utils import (
    ballot_cancellation_suffix,
    date_format,
    is_postponed,
    is_uncontested,
)

# TODO: These might not be right! Implement in uk-election-timetables
#  and think about them harder
TIMETABLE_TYPES = [
    ("PRE_REGISTRATION", "Pre-registration deadline"),
    ("PRE_SOPN", "Pre-candidates nominated"),
    ("POLLING_DAY", "Polling Day"),
]


class ResponseTypes(Enum):
    NO_UPCOMING = "No upcoming elections"
    ONE_CURRENT_BALLOT = "A single upcoming ballot"
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
        self,
        data: Date,
        mode: str,
        current_date: datetime.date,
        timetable,
        response_type: ResponseTypes,
    ) -> None:
        super().__init__()
        self.current_date = current_date
        self.mode = mode
        self.data = data
        self.timetable = timetable
        self.response_type = response_type

    @property
    def weight(self):
        return 0

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def toc_label(self):
        return self.__class__.__name__

    @property
    def toc_id(self):
        return self.__class__.__name__

    @property
    def context(self):
        """
        Holds extra context for this section, useful for template logic
        :return:
        """
        return {}


class PollingStationSection(BaseSection):
    template_name = "includes/polling_station.html"

    @property
    def weight(self):
        poll_date = parse(self.data.date).date()

        days_before_poll = 3
        if (
            poll_date - datetime.timedelta(days=days_before_poll)
        ) < self.current_date:
            return -6000
        return 1003

    @property
    def toc_label(self):
        return _("Where to vote")


class BallotSection(BaseSection):
    template_name = "includes/ballots.html"

    def __init__(self, parish_message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.parish_message = parish_message

    @property
    def weight(self):
        if self.timetable.is_before(TimetableEvent.SOPN_PUBLISH_DATE):
            return 1000

        if self.timetable.is_after(TimetableEvent.SOPN_PUBLISH_DATE):
            return -1000

        return 0

    @cached_property
    def context(self):
        context = super().context
        context["show_candidates"] = self.timetable.is_after(
            TimetableEvent.SOPN_PUBLISH_DATE
        )
        context["sopn_publish_date"] = self.timetable.sopn_publish_date
        context["parish_message"] = self.parish_message
        return context


class PostalVotesSection(BaseSection):
    template_name = "includes/postal_votes.html"

    def __init__(
        self,
        postal_vote_dispatch_dates: List[datetime.date],
        replacement_pack_start_date: datetime.date,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.dispatch_dates = postal_vote_dispatch_dates
        self.replacement_pack_start_date = replacement_pack_start_date

    @property
    def weight(self):
        if self.timetable.is_before(
            TimetableEvent.POSTAL_VOTE_APPLICATION_DEADLINE
        ):
            return -5000

        if self.timetable.is_after(
            TimetableEvent.POSTAL_VOTE_APPLICATION_DEADLINE
        ):
            return 1001
        return 0

    @cached_property
    def context(self):
        context = super().context
        context["can_register"] = self.timetable.is_before(
            TimetableEvent.POSTAL_VOTE_APPLICATION_DEADLINE
        )
        context["dispatch_dates"] = self.dispatch_dates
        context["replacement_pack_start_date"] = (
            self.replacement_pack_start_date
        )

        context["htag_primary"] = "h2"
        context["htag_secondary"] = "h3"
        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            context["htag_primary"] = "h3"
            context["htag_secondary"] = "h4"
        context["toc_id"] = self.toc_id
        return context

    @property
    def toc_label(self):
        return _("Voting by post")

    @property
    def toc_id(self):
        return f"postal-votes-{self.timetable.poll_date}-{self.timetable.postal_vote_application_deadline}"


class RegistrationDateSection(BaseSection):
    template_name = "includes/registration_timetable.html"

    @property
    def weight(self):
        if self.timetable.is_before(TimetableEvent.REGISTRATION_DEADLINE):
            return -6000

        if self.timetable.is_after(TimetableEvent.REGISTRATION_DEADLINE):
            return 1002
        return 0

    @cached_property
    def context(self):
        context = super().context
        context["can_register"] = self.timetable.is_before(
            TimetableEvent.REGISTRATION_DEADLINE
        )
        context["htag_primary"] = "h2"
        context["htag_secondary"] = "h3"
        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            context["htag_primary"] = "h3"
            context["htag_secondary"] = "h4"
        context["toc_id"] = self.toc_id
        return context

    @property
    def toc_label(self):
        return _("Voter registration")

    @property
    def toc_id(self):
        return f"voter-registration-{self.timetable.poll_date}-{self.timetable.registration_deadline}"


class CityOfLondonRegistrationDateSection(RegistrationDateSection):
    template_name = "includes/registration_timetable_city_of_london.html"

    def __init__(self, *args, **kwargs) -> None:
        self.with_headers = kwargs.pop("with_headers")
        super().__init__(*args, **kwargs)

    @property
    def weight(self):
        parent_weight = super().weight
        return 0 if parent_weight == 0 else parent_weight + 1

    @cached_property
    def context(self):
        context = super().context
        context["with_headers"] = self.with_headers
        return context

    @property
    def toc_label(self):
        return _("Voter registration")

    @property
    def toc_id(self):
        return f"voter-registration-col-{self.timetable.poll_date}-{self.timetable.registration_deadline}"


class ElectionDateTemplateSorter:
    def __init__(
        self,
        *,
        date_data: Date,
        country: Country,
        response_type: ResponseTypes,
        current_date: datetime.date = None,
        first_upcoming_date=True,
        postal_vote_dispatch_dates=None,
        replacement_pack_start_date=None,
        in_london: bool = False,
    ) -> None:
        if not current_date:
            current_date = str(datetime.date.today())
        self.current_date = current_date
        self.response_type = response_type

        self.date_data = date_data
        self.first_upcoming_date = first_upcoming_date
        self.ballot_count = len(self.date_data.ballots)
        self.uncancelled_ballot_count = len(
            [b for b in self.date_data.ballots if not b.cancelled]
        )

        self.all_cancelled = all(
            ballot.cancelled for ballot in self.date_data.ballots
        )
        self.cancellation_reasons = {
            ballot.cancellation_reason.name
            for ballot in self.date_data.ballots
            if ballot.cancelled and ballot.cancellation_reason
        }

        # TODO: move to per ballot time tables
        self.timetable = from_election_id(
            self.date_data.ballots[0].election_id, country=country
        )

        self.polling_station_opening_times_str = _("7am – 10pm")
        if any(
            ballot.ballot_paper_id.startswith("local.city-of-london")
            for ballot in self.date_data.ballots
        ):
            self.polling_station_opening_times_str = _("8am – 8pm")

        self.current_mode = None
        for event in self.timetable.timetable:
            if event["date"] <= current_date:
                self.current_mode = event["label"]

        section_kwargs = {
            "data": self.date_data,
            "mode": self.current_mode,
            "response_type": self.response_type,
            "current_date": self.current_date,
            "timetable": self.timetable,
        }

        self.parish_message = ""
        if country == Country.ENGLAND:
            if not in_london:
                self.parish_message = _(
                    "There may also be parish or town council elections in some areas."
                )
        elif country == Country.SCOTLAND:
            self.parish_message = _(
                "There may also be community council elections in some areas."
            )
        elif country == Country.Wales:
            self.parish_message = _(
                "There may also be town or community council elections in some areas."
            )

        enabled_sections = [
            BallotSection(
                **{
                    **section_kwargs,
                    **{"parish_message": self.parish_message},
                }
            )
        ]

        city_of_london_ballots = [
            b
            for b in self.date_data.ballots
            if not b.cancelled
            and b.ballot_paper_id.startswith("local.city-of-london")
        ]
        other_ballots = [
            b
            for b in self.date_data.ballots
            if not b.cancelled
            and not b.ballot_paper_id.startswith("local.city-of-london")
        ]
        if len(other_ballots) > 0:
            enabled_sections.append(
                RegistrationDateSection(
                    data=self.date_data,
                    mode=self.current_mode,
                    response_type=self.response_type,
                    current_date=self.current_date,
                    timetable=from_election_id(
                        other_ballots[0].election_id, country=country
                    ),
                )
            )
        if len(city_of_london_ballots) > 0:
            enabled_sections.append(
                CityOfLondonRegistrationDateSection(
                    data=self.date_data,
                    mode=self.current_mode,
                    response_type=self.response_type,
                    current_date=self.current_date,
                    timetable=from_election_id(
                        city_of_london_ballots[0].election_id, country=country
                    ),
                    with_headers=len(other_ballots) == 0,
                )
            )

        if not self.all_cancelled:
            merged_kwargs = {
                **section_kwargs,
                **{
                    "postal_vote_dispatch_dates": postal_vote_dispatch_dates,
                    "replacement_pack_start_date": replacement_pack_start_date,
                },
            }
            enabled_sections.append(PostalVotesSection(**merged_kwargs))

        if not self.all_cancelled and self.first_upcoming_date:
            enabled_sections.append(PollingStationSection(**section_kwargs))

        self.sections = sorted(enabled_sections, key=lambda sec: sec.weight)


class TemplateSorter:
    """
    Given an API response, sorts template fragments ready for rendering

    """

    def __init__(
        self,
        api_response: RootModel,
        mode=ApiModes.UPCOMING_ELECTIONS,
        current_date: datetime.date = None,
    ) -> None:
        self.current_date = current_date
        if not self.current_date:
            self.current_date = datetime.date.today()
        self.mode = mode
        self.api_response = api_response

        self.total_ballot_count = 0
        self.dates = []
        self.electoral_services = getattr(
            self.api_response, "electoral_services", None
        )
        self.electoral_registration = getattr(
            self.api_response, "registration", None
        )
        for i, date in enumerate(self.api_response.dates):
            postal_vote_dispatch_dates = None
            replacement_pack_start_date = None
            if (
                self.electoral_services
                # we only hold postal votes dispatch data data for one
                # election. TODO: remove/review after 2025-05-01
                and date.date == "2025-05-01"
            ):
                postal_vote_dispatch_dates = get_postal_vote_dispatch_dates(
                    self.electoral_services.council_id
                )
                # hard-coded for May 2025
                # this is the date when replacement packs can be issued from
                # for ALL councils
                # TODO: add this to the timetable library
                replacement_pack_start_date = datetime.datetime.strptime(
                    "25/04/2025", "%d/%m/%Y"
                ).date()

            if parse(date.date).date() < datetime.datetime.today().date():
                continue
            if self.electoral_services:
                country = country_map[self.electoral_services.nation]
            else:
                country = Country.ENGLAND

            in_london = False
            if self.electoral_services:
                in_london = any(
                    id_.startswith("E09")
                    for id_ in self.electoral_services.identifiers
                )

            self.dates.append(
                ElectionDateTemplateSorter(
                    date_data=date,
                    country=country,
                    current_date=self.current_date,
                    response_type=self.response_type,
                    first_upcoming_date=not i > 0,
                    postal_vote_dispatch_dates=postal_vote_dispatch_dates,
                    replacement_pack_start_date=replacement_pack_start_date,
                    in_london=in_london,
                )
            )
            self.total_ballot_count += len(date.ballots)
        self.all_cancelled = all(
            election_date.all_cancelled for election_date in self.dates
        )
        self.all_cancelled_reasons = set()
        for date in self.dates:
            self.all_cancelled_reasons.update(date.cancellation_reasons)

    @property
    def response_type(self):
        if self.mode == ApiModes.CONTACT_DETAILS:
            return ResponseTypes.CONTACT_DETAILS
        if not self.api_response.dates:
            return ResponseTypes.NO_UPCOMING
        if len(self.api_response.dates) == 1:
            if len(self.api_response.dates[0].ballots) == 1:
                return ResponseTypes.ONE_CURRENT_BALLOT
            return ResponseTypes.ONE_CURRENT_DATE
        return ResponseTypes.MULTIPLE_DATES

    @property
    def main_template_name(self):
        # if self.response_type == ResponseTypes.CONTACT_DETAILS:
        #     return "results_contact_details.html"
        if self.response_type == ResponseTypes.NO_UPCOMING:
            return "results_no_upcoming.html"
        if self.response_type == ResponseTypes.ONE_CURRENT_BALLOT:
            return "results_one_current_ballot.html"
        if self.response_type == ResponseTypes.ONE_CURRENT_DATE:
            return "results_one_current_date.html"
        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            return "results_multiple_dates.html"
        raise ValueError("No template selected")

    @property
    def page_title(self):
        """
        Used in the HTML <title> tag and the page's H1 element
        :return:
        """
        if self.mode == ApiModes.CONTACT_DETAILS:
            return _("Contact details")

        if not self.dates:
            return _("There are no upcoming elections in your area")

        if self.all_cancelled:
            cancellation_reasons = self.all_cancelled_reasons
            verbs = []
            if any(is_uncontested(reason) for reason in cancellation_reasons):
                verbs.append(str(_("Uncontested")))

            if any(is_postponed(reason) for reason in cancellation_reasons):
                verbs.append(str(_("Postponed")))

            if not verbs:
                # We don't really know what's going on here
                # so let's assume it's postponed.
                verbs.append(str(_("Postponed")))
            verb = " and ".join(verbs)
            return _(
                f"{verb} election",
                f"{verb} elections",
                count=self.total_ballot_count,
            )

        soonest_date = self.dates[0].date_data.date
        if str(self.current_date) == soonest_date:
            return _("You have an election today")

        if self.response_type == ResponseTypes.ONE_CURRENT_BALLOT:
            return _("You have an upcoming election")

        if self.response_type == ResponseTypes.ONE_CURRENT_DATE:
            return _("You have upcoming elections")

        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            return _("You have upcoming elections")

        return "Elections in your areas"

    @cached_property
    def toc_items(self) -> Optional[List[Dict[str, str]]]:
        """
        Get the table of contents for a response
        """

        if self.response_type == ResponseTypes.ONE_CURRENT_BALLOT:
            return None

        toc = []

        if self.response_type == ResponseTypes.ONE_CURRENT_DATE:
            for section in self.dates[0].sections:
                if isinstance(section, BallotSection):
                    for ballot in section.data.ballots:
                        title = ballot.ballot_title
                        if ballot.cancelled:
                            title = (
                                f"{title}{ballot_cancellation_suffix(ballot)}"
                            )
                        toc.append(
                            {
                                "label": title,
                                "anchor": ballot.ballot_paper_id,
                            }
                        )
                else:
                    toc.append(
                        {"label": section.toc_label, "anchor": section.toc_id}
                    )

        if self.response_type == ResponseTypes.MULTIPLE_DATES:
            for date in self.dates:
                sub_toc = []
                for section in date.sections:
                    if isinstance(section, BallotSection):
                        for ballot in section.data.ballots:
                            sub_toc.append(
                                {
                                    "label": ballot.ballot_title,
                                    "anchor": ballot.ballot_paper_id,
                                }
                            )
                    else:
                        sub_toc.append(
                            {
                                "label": section.toc_label,
                                "anchor": section.toc_id,
                            }
                        )
                toc.append(
                    {
                        "label": date_format(date.date_data.date),
                        "anchor": f"date-{date.date_data.date}",
                        "sub_toc": sub_toc,
                    }
                )

        if toc:
            contact_details_toc = []
            if (
                self.api_response.registration
                == self.api_response.electoral_services
            ):
                contact_details_toc.append(
                    {
                        "label": _("Your local council"),
                        "anchor": "electoral-services",
                    }
                )
            else:
                contact_details_toc.append(
                    {
                        "label": _("Electoral registration"),
                        "anchor": "registration-services",
                    }
                )
                contact_details_toc.append(
                    {
                        "label": _("Your local council"),
                        "anchor": "electoral-services",
                    }
                )

            toc += contact_details_toc
        return toc

    def has_and_parl_ballots(self):
        for date in self.dates:
            for ballot in date.date_data.ballots:
                if ballot.ballot_paper_id.startswith("parl."):
                    return True
        return False
