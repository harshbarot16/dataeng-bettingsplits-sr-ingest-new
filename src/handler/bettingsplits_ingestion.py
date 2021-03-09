""" module containing lambda handler to fetch info of upcoming games """
import json
import urllib.request
import logging
import os
from urllib.error import HTTPError
import datetime
import boto3
from botocore.exceptions import ClientError
import urllib
import urllib.parse
import hashlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_game_ids(event, context):
    """ lambda handler to fetch game ids and their respective schedule start time from Primpy """
    status_code = 500
    endpoint = ""
    message = ""
    try:
        table_name = os.environ["DYNAMODB_TABLE"]
        start_dt = os.environ["START_DT"]
        access_token = os.environ["ACCESS_TOKEN"]
        vendor_token = os.environ["VENDOR_ACCESS_TOKEN"]
        endpoint = os.environ["ENDPOINT"]
        api_key = os.environ["API_KEY"]
        bucket = os.environ["BUCKET"]
    except KeyError as key_error:
        message = "KeyError"
        logger.error("%s", key_error)
    else:
        try:
            str_dt = datetime.datetime.strftime(start_dt, '%Y%m%d')
            end_dt = datetime.datetime.strftime((datetime.datetime.strptime(str_dt, '%Y%m%d') + datetime.timedelta(days=13)), '%Y%m%d')
            args = {"startDate": str_dt, "endDate": end_dt, "access_token": access_token, "fields": "data(gameId,scheduledTime,homeTeam,awayTeam)" }
            api_url = "http://sdf-api.cbssports.cloud/primpy/livescoring/league/games/"+endpoint+"?{}".format(urllib.parse.urlencode(args))
            req = urllib.request.Request(api_url)
            data = json.load(urllib.request.urlopen(req))
        except HTTPError as http_error:
            message = "failed to retrieve game ids for " + endpoint
            logger.error(message)
            logger.error("%s %s", http_error.code, http_error.reason)
            status_code = http_error.code
        except ValueError:
            message = "failed to decode json"
            logger.error(message)
        else:
            try:
                map_args = {"access_token": vendor_token }
                map_url ="http://sdf-api.cbssports.cloud/primpy/highlander/sradar/games/mappings/league/"+endpoint+"?{}".format(urllib.parse.urlencode(map_args))
                req_map = urllib.request.Request(map_url)
                data_map = json.load(urllib.request.urlopen(req_map))
            except HTTPError as http_error:
                message = "failed to retrieve vendor mapping for " + endpoint
                logger.error(message)
                logger.error("%s %s", http_error.code, http_error.reason)
                status_code = http_error.code
            except ValueError:
                message = "failed to decode json"
                logger.error(message)
            else:
                vendor_dict = build_betsplit_file(data,data_map)
                s3 = boto3.client("s3")
                dynamodb = boto3.resource("dynamodb")
                table = dynamodb.Table(table_name)
                result = {}
                for game_id in vendor_dict:
                    final_result, message, status_code = get_betting_insights(result,game_id,vendor_dict,api_key,endpoint)
                status_code, message = dynamodb_hash_check(final_result, endpoint, table, bucket, s3)

    response = {
        "statusCode": status_code,
        "body": endpoint + " completed",
        "message": message,
    }

    return response

def build_betsplit_file(data,data_map):
    """ Map CBS GameId and Get VendorGameId from Primpy API """
    vendor_map = {}
    for game in data['data']:
        game_list = []
        for mappedgames in data_map['mappedGames']:
            if game['gameId']!= mappedgames['cbsGameId']:
                continue
            game_list.append(mappedgames['vendorGameId'])
            game_list.append(game['homeTeam']['teamId'])
            game_list.append(game['awayTeam']['teamId'])
            vendor_map[game['gameId']] = game_list
        if game['gameId'] not in vendor_map.keys():
            message = 'Game mapping not found for GameId: '+str(game['gameId'])
            logger.info(message)
    return vendor_map

def get_betting_insights(result,game_id,vendor_dict,api_key,endpoint):
    """ Get betting splits insights from Sports Radar API"""
    status_code = 500
    message = ""
    try:
        game_args = {"api_key": api_key}
        game_url = "https://api.sportradar.us/bettingsplits/"+endpoint+"/trial/v1/en/game/"+vendor_dict[game_id][0]+"?{}".format(urllib.parse.urlencode(game_args))
        req_game = urllib.request.Request(game_url)
        data_game = json.load(urllib.request.urlopen(req_game))
    except HTTPError as http_error:
        message = "failed to retrieve game info for Game" + str(game_id)+ "and endpoint" + endpoint
        logger.error(message)
        logger.error("%s %s", http_error.code, http_error.reason)
        status_code = http_error.code
    except ValueError:
        message = "failed to decode json"
        logger.error(message)
    else:
        game_ids_concat = str(game_id)+"_"+str(vendor_dict[game_id][1])+"_"+str(vendor_dict[game_id][2])
        result[game_ids_concat] = data_game
        status_code = 200
        message = "json decoded successfully"
    return result, message, status_code

def dynamodb_hash_check(final_result, endpoint, table, bucket, s3):
    try:
        """ Process betting splits data"""
        hexdig = hashlib.md5(json.dumps(final_result).encode()).hexdigest()
        result = table.get_item(Key={"endpoint": endpoint})
    except ClientError as ce:
        status_code = 501
        message = "dynamo get item error"
        logger.error(ce.response["Error"]["Code"])
    else:
        if "Item" in result and "hash_value" in result["Item"]:
            if result["Item"]["hash_value"] != hexdig:
                logger.info("hashes are not equal inserting into s3")
                try:
                    file_name = endpoint
                    s3.put_object(
                        Bucket=bucket, Body=json.dumps(final_result), Key=file_name,
                    )
                except ClientError as ce:
                    status_code = 501
                    message = "s3 put updated object error"
                    logger.error(ce.response["Error"]["Code"])
                else:
                    try:
                        now = str(datetime.datetime.now())
                        result = table.update_item(
                            Key={"endpoint": endpoint},
                            UpdateExpression="SET hash_value=:hash_value, updatedAt=:updatedAt",
                            ExpressionAttributeValues={
                                ":hash_value": hexdig,
                                ":updatedAt": now,
                            },
                        )
                    except ClientError as ce:
                        status_code = 501
                        message = "dynamo update item error"
                        logger.error(ce.response["Error"]["Code"])
                    else:
                        status_code = 200
                        message = "dynamodb item updated with new hash value"
                        logger.info(message)
                        logger.info(hexdig)
            else:
                status_code = 200
                message = "hashes are the same - no update to s3"
                logger.info(message)
                logger.info(hexdig)
        else:
            logger.info("no hash value to check against")
            logger.info("persisting futures response and new hash value")
            try:
                file_name = endpoint
                s3.put_object(
                    Bucket=bucket, Body=json.dumps(final_result), Key=file_name,
                )
            except ClientError as ce:
                status_code = 501
                message = "s3 put new object error"
                logger.error(ce.response["Error"]["Code"])
            else:
                try:
                    result = table.put_item(
                        Item={
                            "endpoint": endpoint,
                            "hash_value": str(hexdig),
                            "updatedAt": str(datetime.datetime.now()),
                        }
                    )
                except ClientError as ce:
                    status_code = 501
                    message = "dynamo put item error"
                    logger.error(ce.response["Error"]["Code"])
                else:
                    status_code = 200
                    message = "dynamodb item created with new hash value"
                    logger.info(message)
                    logger.info(hexdig)

    return status_code, message
