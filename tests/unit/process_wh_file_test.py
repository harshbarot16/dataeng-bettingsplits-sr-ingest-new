""" test process_wh_file errors """
# pylint: disable=invalid-name
import os
import json
from botocore.exceptions import ClientError
import src.handler.get_futures

def test_filtered_object(table, s3, environ):
    """ test filtered object """
    data = json.loads('[{"eventType": "TNMT","id": 2}, {"eventType": "TNMT","id": 4}]')
    endpoint = "test_filter"
    bucket = os.environ["BUCKET"]
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 200
    assert message == "dynamodb item created with new hash value"
    obj = s3.get_object(
                        Bucket=bucket, Key=endpoint,
                    )
    filtered_data = obj['Body'].read().decode('utf-8')
    assert filtered_data == '[{"eventType": "TNMT", "id": 2}, {"eventType": "TNMT", "id": 4}]'

def test_process_wh_file_putitem_error(table, s3, environ):
    """ test put item error """
    data = json.loads('[{"eventType":1}]')
    endpoint = "another_endpoint"
    bucket = os.environ["BUCKET"]
    table.put_item = putitem_error
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 501
    assert message == "dynamo put item error"


def putitem_error(Item):
    """ raise client error """
    error_response = {}
    error_response["Error"] = {}
    error_response["Error"]["Code"] = "ConditionalCheckFailedException"
    raise ClientError(error_response, "PutItem")


def test_process_wh_file_updateitem_error(table, s3, environ):
    """ test update_item error """
    data = json.loads('[{"eventType":2}]')
    endpoint = os.environ["ENDPOINT"]
    bucket = os.environ["BUCKET"]
    table.update_item = updateitem_error
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 501
    assert message == "dynamo update item error"


def updateitem_error(Key, UpdateExpression, ExpressionAttributeValues):
    """ raise update item error """
    error_response = {}
    error_response["Error"] = {}
    error_response["Error"]["Code"] = "ConditionalCheckFailedException"
    raise ClientError(error_response, "UpdateItem")


def test_process_wh_file_putobject_error(table, s3, environ):
    """ test put_object error """
    data = json.loads('[{"eventType":3}]')
    endpoint = os.environ["ENDPOINT"]
    bucket = os.environ["BUCKET"]
    s3.put_object = putobject_error
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 501
    assert message == "s3 put updated object error"


def test_process_wh_file_put_another_object_error(table, s3, environ):
    """ test put_object somewhere else error """
    data = json.loads('[{"eventType":4}]')
    endpoint = "different_endpoint"
    bucket = os.environ["BUCKET"]
    s3.put_object = putobject_error
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 501
    assert message == "s3 put new object error"


def putobject_error(Bucket, Body, Key):
    """ raise client error """
    error_response = {}
    error_response["Error"] = {}
    error_response["Error"]["Code"] = "ConditionalCheckFailedException"
    raise ClientError(error_response, "PutObject")


def test_process_wh_file_getitem_error(table, s3, environ):
    """ test get_item error """
    data = json.loads('[{"eventType":5}]')
    endpoint = os.environ["ENDPOINT"]
    bucket = os.environ["BUCKET"]
    table.get_item = getitem_error
    status_code, message = src.handler.get_futures.process_wh_file(
        data, table, bucket, s3, endpoint
    )
    assert status_code == 501
    assert message == "dynamo get item error"


def getitem_error(Key):
    """ raise get item error """
    error_response = {}
    error_response["Error"] = {}
    error_response["Error"]["Code"] = "ConditionalCheckFailedException"
    raise ClientError(error_response, "UpdateItem")
