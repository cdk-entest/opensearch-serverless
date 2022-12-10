# haimtran 07 DEC 2022
# opensearch serverless

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import os

#
INDEX = 'cdk-entest'

# opensearch domain
if "OPENSEARCH_DOMAIN" in os.environ:
    pass
else:
    os.environ["OPENSEARCH_DOMAIN"] = ""
    os.environ["REGION"] = "us-east-1"

# host and opensearch client
host = os.environ["OPENSEARCH_DOMAIN"]
client = boto3.client("opensearchserverless")
service = "aoss"
region = os.environ["REGION"]
credentials = boto3.Session().get_credentials()

# auth
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)

# opensearch client
client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300,
)


def handler(event, context):
    """
    seach
    """
    for record in event["Records"]:
        id = record["dynamodb"]["Keys"]["id"]["S"]
        if record["eventName"] == "REMOVE":
            pass
        else:
            item = record["dynamodb"]["NewImage"]
            document = {
            "DocumentTitle": item["DocumentTitle"]["S"],
            "DocumentExcerpt": item["DocumentExcerpt"]["S"],
            "DocumentURI": item["DocumentURI"]["S"]
        }
            resp = client.index(
                index=INDEX, id=id, body=document
            )
            print(resp)
    # return
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(resp),
    }
