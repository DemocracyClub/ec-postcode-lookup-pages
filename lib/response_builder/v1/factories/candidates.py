from response_builder.v1.factories.ballots import LocalElectionBallotFactory
from response_builder.v1.factories.base import (
    BaseModelFactory,
    FakerFactoryField,
)
from response_builder.v1.models.base import Candidate, Person, Party


class PersonFactory(BaseModelFactory):
    __model__ = Person

    name = FakerFactoryField("name")


class PartyFactory(BaseModelFactory):
    __model__ = Party


class CandidateFactory(BaseModelFactory):
    __model__ = Candidate

    party = PartyFactory()
    person = PersonFactory()
