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

def test_get_team_future_and_match(environ):
    """ test new item """
    src.handler.get_futures.json.load = json_load_team_future_and_match
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 200
    assert response["body"] == "nfl completed"
    assert response["message"] == "dynamodb item created with new hash value"


def test_get_player_future_and_match(environ):
    """ test different item """
    src.handler.get_futures.json.load = json_load_player_future_and_match
    response = src.handler.get_futures.get_futures(None, None)
    assert response["statusCode"] == 200
    assert response["body"] == "nfl completed"
    assert response["message"] == "dynamodb item updated with new hash value"


def test_get_player_future_again(environ):
    """ test same item """
    src.handler.get_futures.json.load = json_load_player_future_and_match
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


def json_load_player_future_and_match(mockurlopen):
    """ load player future """
    data = json.loads(
        """
        [
        {
            "id": "d0781b22-aeeb-45a2-b0d4-f10a6b594362",
            "name": "Joe Burrow - Your Odds",
            "sportId": "americanfootball",
            "competitionId": "007d7c61-07a7-4e18-bb40-15104b6eac92",
            "competitionName": "NFL",
            "eventType": "TNMT",
            "tradedInPlay": false,
            "started": false,
            "startTime": "2020-09-03T11:00Z",
            "active": true,
            "display": true,
            "expiryDateInMillis": 9223372036854775807,
            "markets": [
                {
                    "id": "0381bcba-de31-41a5-879c-7083bf2c4145",
                    "name": "Your Odds",
                    "line": 0.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "82c43be0-7f0d-4045-be00-5c9a69481ede",
                            "marketId": "0381bcba-de31-41a5-879c-7083bf2c4145",
                            "active": true,
                            "display": true,
                            "name": "Joe Burrow To Be 2020 Offensive Rookie Of The Year",
                            "price": {
                                "a": 225,
                                "d": 3.25,
                                "f": "9/4"
                            }
                        }
                    ]
                }
            ]
        },
        {
            "id": "965c1b22-d185-46e4-80bf-d685135b9ee7",
            "name": "Miami Dolphins at New England Patriots",
            "sportId": "americanfootball",
            "competitionId": "007d7c61-07a7-4e18-bb40-15104b6eac92",
            "competitionName": "NFL",
            "eventType": "MATCH",
            "tradedInPlay": true,
            "started": false,
            "startTime": "2020-09-13T17:00Z",
            "active": true,
            "display": true,
            "expiryDateInMillis": 9223372036854775807,
            "markets": [
                {
                    "id": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                    "name": "Spread",
                    "line": -6.5,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "b234f1cd-f582-3878-b418-93b80aa69fef",
                            "marketId": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                            "active": true,
                            "display": true,
                            "name": "Miami Dolphins",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        },
                        {
                            "id": "788a9894-a89f-3195-9be3-f91be61c12f5",
                            "marketId": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                            "active": true,
                            "display": true,
                            "name": "New England Patriots",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        }
                    ]
                },
                {
                    "id": "17b46260-a010-318a-8193-891ccc9a58ce",
                    "name": "Total Points",
                    "line": 43.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "b1846d9c-49e2-3b9e-abc2-33f730ddcdca",
                            "marketId": "17b46260-a010-318a-8193-891ccc9a58ce",
                            "active": true,
                            "display": true,
                            "name": "Under",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        },
                        {
                            "id": "54e471eb-becd-3633-a56b-c215f126ebd6",
                            "marketId": "17b46260-a010-318a-8193-891ccc9a58ce",
                            "active": true,
                            "display": true,
                            "name": "Over",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        }
                    ]
                },
                {
                    "id": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                    "name": "Money Line",
                    "line": 0.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "bd7cbd4a-bd36-3abd-aad5-727b099d5565",
                            "marketId": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                            "active": true,
                            "display": true,
                            "name": "New England Patriots",
                            "price": {
                                "a": -280,
                                "d": 1.36,
                                "f": "5/14"
                            }
                        },
                        {
                            "id": "ced095e8-9381-335e-bfef-bd926703a829",
                            "marketId": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                            "active": true,
                            "display": true,
                            "name": "Miami Dolphins",
                            "price": {
                                "a": 230,
                                "d": 3.3,
                                "f": "23/10"
                            }
                        }
                    ]
                }
            ]
        }
        ]
        """
    )
    return data


def json_load_team_future_and_match(mockurlopen):
    """ load team future"""
    data = json.loads(
        """
        [
        {
            "id": "27f71aad-3369-3143-aa6c-245fc3b70a5b",
            "name": "Atlanta Falcons To Make The Playoffs",
            "sportId": "americanfootball",
            "competitionId": "007d7c61-07a7-4e18-bb40-15104b6eac92",
            "competitionName": "NFL",
            "eventType": "TNMT",
            "tradedInPlay": false,
            "started": false,
            "startTime": "2020-09-10T23:00Z",
            "active": true,
            "display": true,
            "expiryDateInMillis": 9223372036854775807,
            "markets": [
                {
                    "id": "743cbdf5-149e-3a07-8a96-bc8a8d8b1988",
                    "name": "To Make The Playoffs",
                    "line": 0.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "1bec92b3-f0a2-3ac6-91a4-70e04e7e88f4",
                            "marketId": "743cbdf5-149e-3a07-8a96-bc8a8d8b1988",
                            "active": true,
                            "display": true,
                            "name": "No",
                            "price": {
                                "a": -300,
                                "d": 1.33,
                                "f": "1/3"
                            }
                        },
                        {
                            "id": "7a9ce639-b610-3bcc-b60d-d9a6fb369665",
                            "marketId": "743cbdf5-149e-3a07-8a96-bc8a8d8b1988",
                            "active": true,
                            "display": true,
                            "name": "Yes",
                            "price": {
                                "a": 240,
                                "d": 3.4,
                                "f": "12/5"
                            }
                        }
                    ]
                }
            ]
        },
        {
            "id": "965c1b22-d185-46e4-80bf-d685135b9ee7",
            "name": "Miami Dolphins at New England Patriots",
            "sportId": "americanfootball",
            "competitionId": "007d7c61-07a7-4e18-bb40-15104b6eac92",
            "competitionName": "NFL",
            "eventType": "MATCH",
            "tradedInPlay": true,
            "started": false,
            "startTime": "2020-09-13T17:00Z",
            "active": true,
            "display": true,
            "expiryDateInMillis": 9223372036854775807,
            "markets": [
                {
                    "id": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                    "name": "Spread",
                    "line": -6.5,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "b234f1cd-f582-3878-b418-93b80aa69fef",
                            "marketId": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                            "active": true,
                            "display": true,
                            "name": "Miami Dolphins",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        },
                        {
                            "id": "788a9894-a89f-3195-9be3-f91be61c12f5",
                            "marketId": "2ed7ab2d-81ec-3380-849f-239333228ce0",
                            "active": true,
                            "display": true,
                            "name": "New England Patriots",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        }
                    ]
                },
                {
                    "id": "17b46260-a010-318a-8193-891ccc9a58ce",
                    "name": "Total Points",
                    "line": 43.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "b1846d9c-49e2-3b9e-abc2-33f730ddcdca",
                            "marketId": "17b46260-a010-318a-8193-891ccc9a58ce",
                            "active": true,
                            "display": true,
                            "name": "Under",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        },
                        {
                            "id": "54e471eb-becd-3633-a56b-c215f126ebd6",
                            "marketId": "17b46260-a010-318a-8193-891ccc9a58ce",
                            "active": true,
                            "display": true,
                            "name": "Over",
                            "price": {
                                "a": -110,
                                "d": 1.91,
                                "f": "10/11"
                            }
                        }
                    ]
                },
                {
                    "id": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                    "name": "Money Line",
                    "line": 0.0,
                    "active": true,
                    "display": true,
                    "tradedInPlay": false,
                    "selections": [
                        {
                            "id": "bd7cbd4a-bd36-3abd-aad5-727b099d5565",
                            "marketId": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                            "active": true,
                            "display": true,
                            "name": "New England Patriots",
                            "price": {
                                "a": -280,
                                "d": 1.36,
                                "f": "5/14"
                            }
                        },
                        {
                            "id": "ced095e8-9381-335e-bfef-bd926703a829",
                            "marketId": "64bbb431-ca53-3a7f-bdf5-ae56719f7c4a",
                            "active": true,
                            "display": true,
                            "name": "Miami Dolphins",
                            "price": {
                                "a": 230,
                                "d": 3.3,
                                "f": "23/10"
                            }
                        }
                    ]
                }
            ]
        }
        ]
        """
    )
    return data
