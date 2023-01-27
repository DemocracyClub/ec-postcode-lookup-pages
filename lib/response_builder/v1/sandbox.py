SANDBOX_BASE_URL = "https://developers.democracyclub.org.uk/"
SANDBOX_POSTCODES = {
    "AA11AA": {"description": "No upcoming ballots"},
    "AA12AA": {
        "description": "One upcoming ballot, station known, with candidates"
    },
    "AA12AB": {
        "description": "One upcoming ballot, station not known, with candidates"
    },
    "AA13AA": {
        "description": """
    We need to show the user an address picker. Each of the following /address calls has different polling station info:

    address slug 10035187881
    address slug 10035187882
    address slug 10035187883
    """
    },
    "AA14AA": {
        "description": """
        Four upcoming ballots across 3 future dates with a cancellation:
            * mayor.lewisham.2018-05-03 - Mayoral election
            * local.lewisham.blackheath.2018-05-03 - This election is cancelled and rescheduled on 2018-05-10
            * local.lewisham.blackheath.2018-05-10 - This election replaces the cancelled local.lewisham.blackheath.2018-05-03
            * parl.lewisham-east.by.2018-06-14 - This election is scheduled but we don't know of any candidates yet
    """
    },
    "AA15AA": {
        "description": """
        Northern Ireland. This example shows the custom_finder key in use. We can use this to redirect users to 
        Electoral Office for Northern Ireland's website for polling station data."""
    },
    "EH11YJ": {
        "description": """Scotland. 
        This example shows different registration and electoral services contact details."""
    },
}
