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


def get_futures(event, context):
    """ lambda handler to get william hill futures """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    status_code = 500
    endpoint = ""
    message = ""
    try:
        table_name = os.environ["DYNAMODB_TABLE"]
        endpoint = os.environ["ENDPOINT"]
        bucket = os.environ["BUCKET"]
        wh_api = os.environ["WH_API"]
        x_api_key = os.environ["XAPIKEY"]
    except KeyError as key_error:
        message = key_error
        logger.error("%s", key_error)
    else:
        try:
            print(wh_api)
            print(x_api_key)
            req = urllib.request.Request(wh_api)
            req.add_header("x-api-key", x_api_key)
            data = json.load(urllib.request.urlopen(req))
        except HTTPError as http_error:
            message = "failed to retrieve " + endpoint
            logger.error(message)
            logger.error("%s %s", http_error.code, http_error.reason)
            status_code = http_error.code
        except ValueError:
            message = "failed to decode json"
            logger.error(message)
        else:
            s3 = boto3.client("s3")
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(table_name)
            status_code, message = process_wh_file(data, table, bucket, s3, endpoint)

    response = {
        "statusCode": status_code,
        "body": endpoint + " completed",
        "message": message,
    }

    return response

def process_wh_file(data, table, bucket, s3, endpoint):
    """ process william hill file """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    tnmt_data = [tnmt for tnmt in data if tnmt['eventType'] == 'TNMT']
    hexdig = hashlib.md5(json.dumps(tnmt_data).encode()).hexdigest()
    try:
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
                    s3.put_object(
                        Bucket=bucket, Body=json.dumps(tnmt_data), Key=endpoint,
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
                    Bucket=bucket, Body=json.dumps(tnmt_data), Key=endpoint,
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
