# haimtran 07 DEC 2022
# opensearch serverless

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import os


# opensearch domain
if "OPENSEARCH_DOMAIN" in os.environ:
    pass
else:
    # testing
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
    # parse query from request
    try:
        query_request = event["queryStringParameters"]["query"]
        index = event["queryStringParameters"]["index"]
    except:
        query_request = "ebs"
        index = "cdk-entest"
    # opensearch query
    query = {
        "query": {
            "query_string": {
                "query": query_request
            }
        }
    }
    # response
    resp = client.search(index=index, body=query)
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


if __name__ == "__main__":
    handler(
          event={
            "queryStringParameters": {
                "query": "ebs volume pricing",
                "index": "cdk-entest",
            }
        },
        context=None
    )
