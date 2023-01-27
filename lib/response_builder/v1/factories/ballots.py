from response_builder.v1.factories.base import (
    BaseModelFactory,
    MethodFactoryField,
    FakerFactoryField,
    LiteralFactoryField,
)
from response_builder.v1.factories.faker_providers import (
    LocalBallotDataProvider,
)
from response_builder.v1.models.base import Ballot, VotingSystem


class BaseBallotFactory(BaseModelFactory[Ballot]):
    """
    Can create a ballot, but most of the data in it will be random
    """

    __model__ = Ballot
    __fake_defaults__ = True
    __faker_providers__ = [LocalBallotDataProvider]

    metadata = LiteralFactoryField({})
    ballot_url = FakerFactoryField("ballot_url")
    wcivf_url = FakerFactoryField("wcivf_url")


class LocalElectionBallotFactory(BaseBallotFactory):
    ballot_paper_id = FakerFactoryField("local_ballot_paper_id")
    election_id = FakerFactoryField("local_election_id")
    election_name = FakerFactoryField("local_election_name")
    post_name = FakerFactoryField("ward_name")
    elected_role = LiteralFactoryField("Local Councillor")
    ballot_title = FakerFactoryField("local_ballot_title")
    voting_system = VotingSystem()
