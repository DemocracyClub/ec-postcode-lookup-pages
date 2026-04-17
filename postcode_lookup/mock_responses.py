from response_builder.v1.builders.ballots import (
    BallotBuilder,
    LocalBallotBuilder,
    ParlBallotBuilder,
)
from response_builder.v1.builders.base import RootBuilder
from response_builder.v1.generated_responses import candidates
from response_builder.v1.generated_responses.root_responses import (
    CANCELLED_BALLOT_CANDIDATE_DEATH,
    CANCELLED_BALLOT_EQUAL_CANDIDATES,
    CANCELLED_BALLOT_NO_CANDIDATES,
    CANCELLED_BALLOT_UNDER_CONTESTED,
    MULTIPLE_BALLOTS_WITH_CANCELLATION,
    MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
    NO_LOCAL_BALLOTS,
    ONE_CANCELLED_BALLOT_ONE_NOT,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
    SINGLE_LOCAL_FUTURE_BALLOT_WITHOUT_POLLING_STATION,
)
from response_builder.v1.models.base import (
    Candidate,
    ElectoralServices,
    EmailStr,
    Party,
    Person,
    Registration,
)


class CityOfLondonParlBallot(ParlBallotBuilder):
    def __init__(self, poll_open_date, **kwargs):
        super().__init__(**kwargs)
        self.with_ballot_paper_id(
            f"parl.cities-of-london-and-westminster.{poll_open_date}"
        )
        self.with_ballot_title(
            "UK Parliamentary general election Cities of London and Westminster"
        )
        self.with_date(poll_open_date)
        self.with_post_name("Cities of London and Westminster")
        self.with_election_name("UK Parliamentary general election")
        self.with_election_id(f"parl.{poll_open_date}")
        self.with_candidates(candidates.all_candidates)


class CityOfLondonLocalBallot(LocalBallotBuilder):
    def __init__(self, poll_open_date, **kwargs):
        super().__init__(**kwargs)
        self.with_ballot_paper_id(
            f"local.city-of-london.aldersgate.{poll_open_date}"
        )
        self.with_ballot_title("City of London local election Aldersgate")
        self.with_date(poll_open_date)
        self.with_post_name("Aldersgate")
        self.with_election_name("City of London local election")
        self.with_election_id(f"local.city-of-london.{poll_open_date}")
        self.with_candidates(candidates.all_candidates)


class SeneddBallot(BallotBuilder):
    def __init__(self, poll_open_date, **kwargs):
        super().__init__(**kwargs)
        self.with_ballot_paper_id(f"senedd.gwyr-abertawe.{poll_open_date}")
        self.with_ballot_title("Gŵyr Abertawe")
        self.with_date(poll_open_date)
        self.with_post_name("Gŵyr Abertawe")
        self.with_election_name("Senedd Cymru elections")
        self.with_election_id(f"senedd.{poll_open_date}")
        self.with_elected_role("Member of the Senedd")
        self.with_voting_system("PR-CL")
        # Add two independent candidates
        self.with_candidates(
            candidates.all_candidates
            + [
                Candidate(
                    list_position=1,
                    party=Party(
                        party_name="Independent",
                        party_id="ynmp-party:2",
                    ),
                    person=Person(
                        name="Ms. Qux Baz",
                        ynr_id=101112,
                        absolute_url="https://candidates.democracyclub.org.uk/person/101112",
                        email=EmailStr("independent1@example.com"),
                        photo_url="https://s3.eu-west-2.amazonaws.com/static-candidates.democracyclub.org.uk/media/cache/fc/101112/fc101112.jpg",
                    ),
                ),
                Candidate(
                    list_position=1,
                    party=Party(
                        party_name="Independent",
                        party_id="ynmp-party:2",
                    ),
                    person=Person(
                        name="Ms. Qux Norf",
                        ynr_id=101113,
                        absolute_url="https://candidates.democracyclub.org.uk/person/101113",
                        email=EmailStr("independent2@example.com"),
                        photo_url="https://s3.eu-west-2.amazonaws.com/static-candidates.democracyclub.org.uk/media/cache/fc/101112/fc101112.jpg",
                    ),
                ),
            ]
        )


class SPConstituencyBallot(BallotBuilder):
    def __init__(self, poll_open_date, **kwargs):
        super().__init__(**kwargs)
        self.with_ballot_paper_id(f"sp.c.shetland-islands.{poll_open_date}")
        self.with_ballot_title(
            "Scottish Parliament elections (Constituencies) Shetland Islands"
        )
        self.with_date(poll_open_date)
        self.with_post_name("Shetland Islands")
        self.with_election_name(
            "Scottish Parliament elections (Constituencies)"
        )
        self.with_election_id(f"sp.c.{poll_open_date}")
        self.with_elected_role("Member of the Scottish Parliament")
        self.with_voting_system("FPTP")
        self.with_candidates(candidates.all_candidates)


class SPRegionBallot(BallotBuilder):
    def __init__(self, poll_open_date, **kwargs):
        super().__init__(**kwargs)
        self.with_ballot_paper_id(
            f"sp.r.highlands-and-islands.{poll_open_date}"
        )
        self.with_ballot_title(
            "Scottish Parliament elections (Regions) Highlands and Islands"
        )
        self.with_date(poll_open_date)
        self.with_post_name("Highlands and Islands")
        self.with_election_name("Scottish Parliament elections (Regions)")
        self.with_election_id(f"sp.r.{poll_open_date}")
        self.with_elected_role("Member of the Scottish Parliament")
        self.with_voting_system("AMS")
        self.with_candidates(candidates.all_candidates)


CITY_OF_LONDON_COUNCIL_AND_PARL_DIFFERENT_DAYS = (
    RootBuilder()
    .with_ballot(CityOfLondonLocalBallot("2025-03-20").build())
    .with_ballot(CityOfLondonParlBallot("2025-05-01").build())
)
CITY_OF_LONDON_COUNCIL_AND_PARL_SAME_DAY = (
    RootBuilder()
    .with_ballot(CityOfLondonLocalBallot("2025-03-20").build())
    .with_ballot(CityOfLondonParlBallot("2025-03-20").build())
)
SENEDD_2026_ONWARDS_BALLOT = RootBuilder().with_ballot(
    SeneddBallot("2025-03-20").build()
)
SENEDD_2026_ONWARDS_BALLOT.set(
    "electoral_services",
    ElectoralServices(
        council_id="SWA",
        name="City & County of Swansea",
        address="Electoral Services\r\nGuildhall\r\nSwansea",
        email="elections@swansea.gov.uk",
        nation="Wales",
        phone="123456",
        postcode="SA1 4PE",
        website="https://www.swansea.gov.uk/",
        identifiers=["W06000011"],
    ),
)
SCOTTISH_PARLIAMENT_BALLOTS = (
    RootBuilder()
    .with_ballot(SPConstituencyBallot("2025-03-20").build())
    .with_ballot(SPRegionBallot("2025-03-20").build())
)
SCOTTISH_PARLIAMENT_BALLOTS.set(
    "electoral_services",
    ElectoralServices(
        council_id="EDH",
        name="City of Edinburgh Council",
        address="City Chambers\r\nHigh Street\r\nEdinburgh",
        email="elections@edinburgh.gov.uk",
        nation="Scotland",
        phone="123456",
        postcode="EH1 1YJ",
        website="https://www.edinburgh.gov.uk",
        identifiers=["S12000036"],
    ),
)
SCOTTISH_PARLIAMENT_BALLOTS.set(
    "registration",
    Registration(
        phone="123456",
        email="enquiries@lothian-vjb.gov.uk",
        address="Electoral Registration Officer\nLothian Valuation Joint Board\n17A South Gyle Crescent\nEDINBURGH",
        postcode="EH12 9FL",
        website="http://www.lothian-vjb.gov.uk/",
    ),
)


__ALL__ = ("example_responses",)
example_responses = {
    "AA1 1AA": {
        "description": "No local ballots",
        "response": NO_LOCAL_BALLOTS,
    },
    "CA1 1AB": {
        "description": "Cancelled ballot due to candidate death",
        "response": CANCELLED_BALLOT_CANDIDATE_DEATH,
    },
    "CA1 2AB": {
        "description": "Cancelled ballot due to no candidates",
        "response": CANCELLED_BALLOT_NO_CANDIDATES,
    },
    "CA1 3AB": {
        "description": "Cancelled ballot due to equal number of candidates",
        "response": CANCELLED_BALLOT_EQUAL_CANDIDATES,
    },
    "CA1 4AB": {
        "description": "Cancelled ballot due to not enough candidates",
        "response": CANCELLED_BALLOT_UNDER_CONTESTED,
    },
    "CA1 5AB": {
        "description": "One cancelled ballot, one not cancelled",
        "response": ONE_CANCELLED_BALLOT_ONE_NOT,
    },
    "AA1 1AC": {
        "description": "Single local ballot (One upcoming ballot, station known, with candidates)",
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
    },
    "AA1 1AD": {
        "description": "Single local ballot (One upcoming ballot, station not known, with candidates)",
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITHOUT_POLLING_STATION,
    },
    "AA1 1AF": {
        "description": "Multiple ballots including Greater London Assembly and Mayoral with voting system and polling station",
        "response": MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
    },
    "AA1 1AG": {
        "description": "Multiple ballots including a Local, GLA, Mayoral, Parliamentary ballots including one cancellation.",
        "response": MULTIPLE_BALLOTS_WITH_CANCELLATION,
    },
    # "AA1 1AH": {
    #     "description": "Parliamentary ballot",
    #     "response": PARL_BALLOT,
    # },
    # "AA1 1AI": {
    #     "description": "London Assembly ballot",
    #     "response": GLA_BALLOT,
    # },
    # "AA1 1AJ": {
    #     "description": "Mayoral ballot",
    #     "response": MAYORAL_BALLOT,
    # },
    # "AA1 1AK": {
    #     "description": "Police and Crime Commissioner ballot",
    #     "response": PCC_BALLOT,
    # },
    "AA1 1AL": {
        "description": "City of London (Common Councilman) and UK Parl ballots on different upcoming dates",
        "response": CITY_OF_LONDON_COUNCIL_AND_PARL_DIFFERENT_DAYS,
    },
    "AA1 1AM": {
        "description": "City of London (Common Councilman) and UK Parl ballots on the same date",
        "response": CITY_OF_LONDON_COUNCIL_AND_PARL_SAME_DAY,
    },
    "AA1 1AN": {
        "description": "Senedd (2026 onwards) ballot. Party list election with multiple independent candidates",
        "response": SENEDD_2026_ONWARDS_BALLOT,
    },
    "AA1 1AP": {
        "description": "Scottish parliament ballots: FPTP Constituency ballot and Party list Region ballot on same date. Also features different registration and electoral services contact details",
        "response": SCOTTISH_PARLIAMENT_BALLOTS,
    },
}
