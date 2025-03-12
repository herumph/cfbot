from query.common import call_espn


def test_call_espn_good_url():
    """Test the generic call function with a good url."""
    response = call_espn("https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard")
    assert response


def test_call_espn_no_json_response():
    """Test the generic call function with a url that doesn't have a json
    response."""
    response = call_espn("https://espn.com")
    assert response is None
