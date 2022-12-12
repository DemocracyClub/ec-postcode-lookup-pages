from typing import Dict, Union, Optional

from pydantic import BaseModel, Field


class AdvanceVotingStation(BaseModel):
    ...


class Station(BaseModel):
    """
    GeoJSON formatted information about a polling station.

    """

    id: str = Field(
        default_factory=str, description="A unique ID for this polling station"
    )

    urls: Dict = Field(
        default_factory=dict,
        description=(
            "A dict containing detail and geoJSON details of this polling station"
        ),
    )
    station_id: str = Field(
        default_factory=str,
        description="The council provided ID for this polling sation",
    )
    postcode: Union[str, None] = Field(
        default_factory=None,
        description="The postcode of the polling station, if available",
        nullable=True,
    )


class PollingStation(BaseModel):
    polling_station_known: bool = Field(
        default=False,
        description="True if we have polling station data for this request",
    )
    custom_finder: Optional[str] = Field(
        default=None,
        description=(
            "If not none: there is another polling sation finder for this "
            "request. Direct your users there so they can find where to vote"
        ),
    )
    report_problem_url: Optional[str] = Field(
        default_factory=str,
        description="HTML form for reporting problems with the polling station data",
    )
    station: Optional[Station] = Field(
        default=None, description="Details about the polling station"
    )
