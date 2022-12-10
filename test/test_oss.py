# haimtran 07 DEC 2022
# opensearch serverless

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import os
import uuid


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
    # parse query from request
    try:
        query_request = event["queryStringParameters"]["query"]
        index = event["queryStringParameters"]["index"]
    except:
        query_request = "ebs"
        index = "cdk-entest"
    # opensearch query
    query = {"query": {"query_string": {"query": "Hello"}}}
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


def test_index_data(index_name):
    """
    test index a document into the opensearch serverless
    """
    #
    response = client.index(
        index=index_name,
        # body={"title": "pricing", "creator": "Larry David", "year": 1989},
       body={
            "DocumentTitle": "pricing",
            "DocumentExcerpt": "100",
            "DocumentURI":"URL"
        },
        id=str(uuid.uuid4()),
    )
    print(response)


def test_query_index(query):
    """
    test query from opensearch serverless
    """
    response = client.search(
        index="cdk-entest", body={"query": {"query_string": {"query": query}}}
    )
    print(response)


def test_index_complex(item):
    """
    indx opensearch serverless
    """
    resp = client.index(
        index="cdk-entest",
        id=str(uuid.uuid4()),
        body={
            "DocumentTitle": item["DocumentTitle"],
            "DocumentExcerpt": item["DocumentExcerpt"],
            "DocumentURI": item["DocumentURI"]
        },
    )
    print(resp)


def test_query_complex(query_request):
    """
    query opensearch
    """
    resp = client.search(
        index="cdk-entest",
        body={
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
        },
    )
    print(resp)



def delete_index(index_name):
    """
    delete index
    """
    resp = client.indices.delete(
        index=index_name
    )
    print(resp)


def create_index(index_name):
    """
    craete index
    """
    resp = client.indices.create(index_name)
    print(resp)


def delete_document(id, index_name):
    """
    """
    resp = client.delete(
        index=index_name,
        id=id
    )
    print(resp)



if __name__ == "__main__":
    # test_query_index(query="pricing")
    # handler(
    #       event={
    #         "queryStringParameters": {
    #             "query": "Hello",
    #             "index": "cdk-entest",
    #         }
    #     },
    #     context=None
    # )
    # test_index_complex(
    #     item={
    #         "DocumentTitle": "ebs",
    #         "DocumentExcerpt": "this is a good information",
    #         "DocumentURI": "uri",
    #     }
    # )
    # test_query_complex(
    #     "ebs"
    # )
    # delete_index(index_name="cdk-entest")
    # create_index(index_name="cdk-entest")
    # test_index_data(index_name="cdk-entest")
    delete_document(id = "5164d1fe-9b3e-4e67-afa1-b62f7bb330fc", index_name="cdk-entest")
