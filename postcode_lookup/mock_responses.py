from response_builder.v1.generated_responses.root_responses import (
    CANCELLED_BALLOT,
    NO_LOCAL_BALLOTS,
    RECENTLY_PASSED_LOCAL_BALLOT,
    # LOCAL_BALLOT_WITH_ID_REQUIREMENTS,
    GLA_BALLOT,
    MAYORAL_BALLOT,
    PARL_BALLOT,
    PCC_BALLOT,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
    SINGLE_LOCAL_FUTURE_BALLOT_WITHOUT_POLLING_STATION,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_ADDRESS_PICKER,
    MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
    MULTIPLE_BALLOTS_WITH_CANCELLATION,
)

__ALL__ = ("example_responses",)
example_responses = {
    "AA1 1AA": {
        "description": "No local ballots",
        "response": NO_LOCAL_BALLOTS,
    },
    "AA1 1AB": {
        "description": "Cancelled ballot",
        "response": CANCELLED_BALLOT,
    },
    "AA1 1BB": {
        "description": "Recently passed local ballot", 
        "response": RECENTLY_PASSED_LOCAL_BALLOT,
    },
    # "AA1 1AZ": {
    #     "description": "Single local ballot with ID requirements",
    #     "response": LOCAL_BALLOT_WITH_ID_REQUIREMENTS,
    # }, 
    "AA1 1AC": {
        "description": "Single local ballot (One upcoming ballot, station known, with candidates)",
        # needs candidates
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
    },
    "AA1 1AD": {
        "description": "Single local ballot (One upcoming ballot, station not known, with candidates)",
        # needs candidates
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITHOUT_POLLING_STATION,
    }, 
    "AA1 1AE": {
        "description": "Single local ballot (One upcoming ballot, station not known, with address picker)",
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITH_ADDRESS_PICKER,
    },
    "AA1 1AF": {
        "description": "Multiple ballots including Greater London Assembly and Mayoral with voting system and polling station",
        # needs candidates
        "response": MULTIPLE_BALLOTS_WITH_VOTING_SYSTEM_AND_POLLING_STATION,
    },
    "AA1 1AG": {
        "description": "Multiple ballots including a Local, GLA, Mayoral, Parliamentary ballots including one cancellation.",
        "response": MULTIPLE_BALLOTS_WITH_CANCELLATION,
    }, 
    "AA1 1AH": {
        "description": "Parliamentary ballot",
        "response": PARL_BALLOT,
    },
    "AA1 1AI": {
        "description": "London Assembly ballot",
        "response": GLA_BALLOT,
    },
    "AA1 1AJ": {
        "description": "Mayoral ballot",
        "response": MAYORAL_BALLOT,
    },
    "AA1 1AK": {
        "description": "Police and Crime Commissioner ballot",
        "response": PCC_BALLOT,
    },
}
