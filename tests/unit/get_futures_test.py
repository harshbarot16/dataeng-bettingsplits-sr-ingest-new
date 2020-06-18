""" test get_futures """
import json
from urllib.error import HTTPError
import src.handler.get_futures


def test_get_wh_keyerror():
    """ test keyerror """
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 500
    assert response["body"] == " completed"
    assert response["message"] == "KeyError"


def test_get_wh_valueerror(environ):
    """ test value error """
    src.handler.get_futures.json.load = json_load_value_error
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 500
    assert response["body"] == "nfl completed"
    assert response["message"] == "failed to decode json"


def json_load_value_error(urlopen):
    """ raise value error """
    raise ValueError


def test_get_team_future(environ):
    """ test new item """
    src.handler.get_futures.json.load = json_load_team_future
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 200
    assert response["body"] == "nfl completed"
    assert response["message"] == "dynamodb item created with new hash value"


def test_get_player_future(environ):
    """ test different item """
    src.handler.get_futures.json.load = json_load_player_future
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 200
    assert response["body"] == "nfl completed"
    assert response["message"] == "dynamodb item updated with new hash value"


def test_get_player_future_again(environ):
    """ test same item """
    src.handler.get_futures.json.load = json_load_player_future
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 200
    assert response["body"] == "nfl completed"
    assert response["message"] == "hashes are the same - no update to s3"


def test_get_futures_httperror(environ):
    """ test http error """
    src.handler.get_futures.urllib.request.urlopen = url_open_http_error
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 403
    assert response["body"] == "nfl completed"
    assert response["message"] == "failed to retrieve nfl"


def url_open_http_error(urlopen):
    """ raise http error """
    raise HTTPError("url", 403, "Forbidden", "hdrs", "fp")


def json_load_player_future(mockurlopen):
    """ load player future """
    data = json.loads(
        """

        """
    )
    return data


def json_load_team_future(mockurlopen):
    """ load team future"""
    data = json.loads(
        """
    {
        "id": "2a40c9f1-f906-3852-9c6d-2b2b79ae6078",
        "name": "2020 AFC East Winner",
        "sportId": "americanfootball",
        "competitionId": "007d7c61-07a7-4e18-bb40-15104b6eac92",
        "competitionName": "NFL",
        "eventType": "TNMT",
        "tradedInPlay": false,
        "started": false,
        "startTime": "2020-09-09T23:00Z",
        "active": true,
        "display": true,
        "expiryDateInMillis": 9223372036854775807,
        "markets": [
            {
                "id": "1feed306-ed70-3f93-a30d-b9ccc624079b",
                "name": "Division Winner",
                "line": 0.0,
                "active": true,
                "display": true,
                "tradedInPlay": false,
                "selections": [
                    {
                        "id": "73114971-37ae-3e7a-b587-65381e11314a",
                        "marketId": "1feed306-ed70-3f93-a30d-b9ccc624079b",
                        "active": true,
                        "display": true,
                        "name": "New York Jets",
                        "price": {
                            "a": 750,
                            "d": 8.5,
                            "f": "15/2"
                        }
                    },
                    {
                        "id": "5a1b78d5-ce50-3fdf-a2b8-6dc078074857",
                        "marketId": "1feed306-ed70-3f93-a30d-b9ccc624079b",
                        "active": true,
                        "display": true,
                        "name": "Miami Dolphins",
                        "price": {
                            "a": 750,
                            "d": 8.5,
                            "f": "15/2"
                        }
                    },
                    {
                        "id": "9512c3a3-3543-3700-9f20-a6db9bdb4a6e",
                        "marketId": "1feed306-ed70-3f93-a30d-b9ccc624079b",
                        "active": true,
                        "display": true,
                        "name": "New England Patriots",
                        "price": {
                            "a": 120,
                            "d": 2.2,
                            "f": "6/5"
                        }
                    },
                    {
                        "id": "fce5c573-2ff8-3147-9802-9de8d73423fe",
                        "marketId": "1feed306-ed70-3f93-a30d-b9ccc624079b",
                        "active": true,
                        "display": true,
                        "name": "Buffalo Bills",
                        "price": {
                            "a": 130,
                            "d": 2.3,
                            "f": "13/10"
                        }
                    }
                ]
            }
        ]
    }
        """
    )
    return data
