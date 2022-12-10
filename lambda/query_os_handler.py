"""
haimtran 05/11/2022
lambda opensearch
"""

import json
import os
import boto3
from opensearchpy import (
    OpenSearch,
    RequestsHttpConnection,
    AWSV4SignerAuth,
)

# opensearch domain
if "OPENSEARCH_DOMAIN" in os.environ:
    OPENSEARCH_DOMAIN = os.environ["OPENSEARCH_DOMAIN"]
else:
    # testing
    OPENSEARCH_DOMAIN = ""
    os.environ["REGION"] = "us-east-1"

# get credential
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region=os.environ["REGION"])

# create opensearch client
client = OpenSearch(
    hosts=[
        {
            "host": OPENSEARCH_DOMAIN,
            "port": 443,
        }
    ],
    use_ssl=True,
    verify_certs=True,
    http_auth=auth,
    connection_class=RequestsHttpConnection,
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
        # 'size': 10,
        "query": {
            "multi_match": {
                "query": query_request,
                "fields": [
                    "DocumentTitle",
                    "DocumentExcerpt",
                    "DocumentURI",
                ],
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
    resp_test = handler(
        event={
            "queryStringParameters": {
                "query": "ebs",
                "index": "cdk-entest",
            }
        },
        context=None,
    )
    print(resp_test)
