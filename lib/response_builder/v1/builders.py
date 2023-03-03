from typing import Optional

from faker import Faker
from pydantic import BaseModel

from response_builder.v1.factories.ballots import LocalElectionBallotFactory
from response_builder.v1.factories.base import (
    BaseModelFactory,
    RootModelFactory,
)
from response_builder.v1.factories.candidates import CandidateFactory
from response_builder.v1.factories.councils import ElectoralServicesFactory
from response_builder.v1.models.base import Date, Ballot
from response_builder.v1.models.councils import ElectoralServices


class AbstractBuilder:
    model: Optional[BaseModel] = None
    factory: BaseModelFactory = None

    def __init__(self, model=None, **kwargs):
        self.kwargs = kwargs
        self._factory = self.factory()

    def build(self, **kwargs) -> BaseModel:
        return self._factory.build(**kwargs)


class RootBuilder(AbstractBuilder):
    factory = RootModelFactory

    def __init__(self):
        super().__init__()
        self.faker = Faker()
        self.factory.electoral_services = ElectoralServicesFactory().build()

    def with_address_picker(self):
        self.factory.address_picker = True
        return self

    def with_date(
        self, date: Optional[str] = None, date_model: Optional[Date] = None
    ):
        if all([date, date_model]):
            raise ValueError("Either specify `date` or `date_model`, not both.")
        if date:
            date_model = Date(date=date)

        self.factory.__model__.dates.append(date_model)
        return self

    def with_ballot(self, ballot_model: Ballot):
        ballot_date = ballot_model.ballot_paper_id.split(".")[-1]
        if ballot_date not in self.factory.__model__.dates:
            self.with_date(ballot_date)
        for date_model in self.factory.__model__.dates:
            if date_model.date == ballot_date:
                date_model.ballots.append(ballot_model)

    def with_electoral_services(self, electoral_services: ElectoralServices):
        self.factory.__model__.electoral_services = electoral_services
        if not self.factory.__model__.registration:
            self.factory.registration = electoral_services

    def build(self):
        return self.factory.__model__


class BallotBuilder(AbstractBuilder):
    pass


class LocalBallotBuilder(BallotBuilder):
    factory: Ballot = LocalElectionBallotFactory

    def with_candidates(self, count, verified=False):
        self.factory.candidates_verified = verified
        self.factory.seats_contested = 1
        for i in range(count):
            self.with_candidate()
        return self

    def with_candidate(self, candidate=None, **kwargs):
        if not candidate:
            candidate = CandidateFactory().build(**kwargs)
        if not hasattr(self.factory, "candidates"):
            self.factory.candidates = []
        self.factory.candidates.append(candidate)
        return self
