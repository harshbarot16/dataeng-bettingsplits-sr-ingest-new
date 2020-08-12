""" pytest fixtures """
import os
import pytest
import boto3
from moto import mock_s3
from moto import mock_dynamodb2


@pytest.fixture(name="aws_credentials", scope="session", autouse=True)
def fix_aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(name="s3", scope="session", autouse=True)
def fix_s3():
    """ s3 """
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="futures-wh-sls")
        yield s3


@pytest.fixture(name="table", scope="session", autouse=True)
def fix_dynamodb():
    """ dynamodb """
    with mock_dynamodb2():
        boto3.client("dynamodb").create_table(
            TableName="wh-endpoint-hash-table",
            KeySchema=[{"AttributeName": "endpoint", "KeyType": "HASH"},],
            AttributeDefinitions=[{"AttributeName": "endpoint", "AttributeType": "S"},],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        yield boto3.resource("dynamodb", region_name="us-east-1").Table(
            "wh-endpoint-hash-table"
        )


@pytest.fixture(name="environ", scope="session")
def fix_environ():
    """ environ """
    os.environ["DYNAMODB_TABLE"] = "wh-endpoint-hash-table"
    os.environ["ENDPOINT"] = "nfl"
    os.environ["BUCKET"] = "futures-wh-sls"
    os.environ["WH_COMP_API"] = "https://odds.us.williamhill.com/api/v1/events?competitionId=007d7c61-07a7-4e18-bb40-15104b6eac92"
    os.environ["WH_EVENT_API"] = "https://odds.us.williamhill.com/api/v1/events?eventId="
    os.environ["XAPIKEY"] = "XbiOHGfBxxvSmXBQdb6vF3gZ9P3DWUgHVmmrRpSe"
