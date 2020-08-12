""" module containing lambda handler to get william hill futures """
import json
import urllib.request
import logging
import os
from urllib.error import HTTPError
import datetime
import hashlib
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_futures(event, context):
    """ lambda handler to get william hill futures """
    status_code = 500
    endpoint = ""
    message = ""
    try:
        table_name = os.environ["DYNAMODB_TABLE"]
        endpoint = os.environ["ENDPOINT"]
        bucket = os.environ["BUCKET"]
        wh_comp_api = os.environ["WH_COMP_API"]
        wh_event_api = os.environ["WH_EVENT_API"]
        x_api_key = os.environ["XAPIKEY"]
    except KeyError as key_error:
        message = "KeyError"
        logger.error("%s", key_error)
    else:
        try:
            req = urllib.request.Request(wh_comp_api)
            req.add_header("x-api-key", x_api_key)
            data = json.load(urllib.request.urlopen(req))
        except HTTPError as http_error:
            message = "failed to retrieve events by competition for " + endpoint
            logger.error(message)
            logger.error("%s %s", http_error.code, http_error.reason)
            status_code = http_error.code
        except ValueError:
            message = "failed to decode json"
            logger.error(message)
        else:
            status_code, message, file_data = build_wh_file(data, wh_event_api, x_api_key)
            if status_code == 200:
                s3 = boto3.client("s3")
                dynamodb = boto3.resource("dynamodb")
                table = dynamodb.Table(table_name)
                status_code, message = process_wh_file(file_data, table, bucket, s3, endpoint)

    response = {
        "statusCode": status_code,
        "body": endpoint + " completed",
        "message": message,
    }

    return response

def build_wh_file(data, wh_event_api, x_api_key):
    """ build file from active tnmt events """
    tnmt_data = [tnmt for tnmt in data if tnmt['eventType'] == 'TNMT' and tnmt['active']]
    return_data = []
    status_code = 200
    message = 'success'
    for event in tnmt_data:
        logger.info(event['name'])
        try:
            endpoint = wh_event_api + str(event['id'])
            req = urllib.request.Request(endpoint)
            req.add_header("x-api-key", x_api_key)
            data = json.load(urllib.request.urlopen(req))
        except HTTPError as http_error:
            message = "failed to retrieve event for " + endpoint
            logger.error(message)
            logger.error("%s %s", http_error.code, http_error.reason)
            status_code = http_error.code
        except ValueError:
            status_code = 500
            message = "failed to decode json"
            logger.error(message)
        else:
            return_data.append(data[0])
    return status_code, message, return_data

def process_wh_file(data, table, bucket, s3, endpoint):
    """ process william hill file """
    # endpoint += "_test1"
    hexdig = hashlib.md5(json.dumps(data).encode()).hexdigest()
    try:
        result = table.get_item(Key={"endpoint": endpoint})
    except ClientError as ce:
        status_code = 501
        message = "dynamo get item error"
        logger.error(ce.response["Error"]["Code"])
        logger.error(ce.response["Error"]["Message"])
    else:
        if "Item" in result and "hash_value" in result["Item"]:
            if result["Item"]["hash_value"] != hexdig:
                logger.info("hashes are not equal inserting into s3")
                try:
                    s3.put_object(
                        Bucket=bucket, Body=json.dumps(data), Key=endpoint,
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
                s3.put_object(
                    Bucket=bucket, Body=json.dumps(data), Key=endpoint,
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
