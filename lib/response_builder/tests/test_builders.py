from response_builder.v1.builders import RootBuilder, LocalBallotBuilder
from response_builder.v1.factories.ballots import LocalElectionBallotFactory
from response_builder.v1.factories.councils import NuneatonElectoralServices
from response_builder.v1.models.base import Ballot


def test_builder():
    builder = RootBuilder()
    ballot1 = LocalBallotBuilder()
    ballot1.with_candidates(3)
    builder.with_ballot(ballot1.build())
    # builder.with_ballot(ballot2)
    builder.with_electoral_services(NuneatonElectoralServices)
    print(builder.build().json(indent=4))
