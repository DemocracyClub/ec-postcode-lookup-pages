from multiprocessing import Process
from random import randrange

import pytest
import uvicorn
from app import app
from starlette.testclient import TestClient
from template_sorter import (
    ApiModes,
    ElectionDateTemplateSorter,
    TemplateSorter,
)
from uk_election_timetables.calendars import Country
from uk_election_timetables.election_ids import from_election_id


@pytest.fixture(scope="function")
def app_client() -> TestClient:
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
def uvicorn_server():
    port = randrange(8010, 8100)
    proc = Process(
        target=uvicorn.run,
        args=("app:app",),
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "workers": 1,
            "access_log": False,
            "log_level": "critical",
        },
    )
    proc.start()
    import time

    time.sleep(0.3)
    yield f"http://localhost:{port}"
    proc.kill()


@pytest.fixture
def template_sorter():
    def get_template_sorter(mock_response, date):
        api_response = mock_response
        # The dates exist in the api_response, but not
        # in the format that matches the RootBuilder:
        # dates = api_response._values["dates"] vs
        # dates = api_response.dates so I've set it here.
        api_response.dates = api_response._values["dates"]
        mode = ApiModes.UPCOMING_ELECTIONS

        sorter = TemplateSorter(
            api_response=api_response, mode=mode, current_date=date
        )
        sorter.country = Country.ENGLAND
        sorter.dates = api_response.dates

        return sorter

    return get_template_sorter


@pytest.fixture
def election_date_template_sorter():
    def get_election_date_template_sorter(template_sorter, date):
        election_date_sorter = ElectionDateTemplateSorter(
            date_data=date,
            country=template_sorter.country,
            current_date=template_sorter.current_date,
            response_type=template_sorter.response_type,
        )
        election_date_sorter.current_date = template_sorter.current_date

        election_date_sorter.timetable = from_election_id(
            template_sorter.dates[0].ballots[0].election_id,
            country=template_sorter.country,
        )

        return election_date_sorter

    return get_election_date_template_sorter
