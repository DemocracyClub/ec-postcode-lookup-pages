from response_builder.v1.generated_responses.root_responses import (
    NO_LOCAL_BALLOTS,
    SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
)

__ALL__ = ("example_responses",)

example_responses = {
    "MM1 1AA": {
        "description": "Single local ballot",
        "response": SINGLE_LOCAL_FUTURE_BALLOT_WITH_POLLING_STATION,
    "MM1 1AC": {
        "description": "No local ballots",
        "response": NO_LOCAL_BALLOTS,
    },
}
