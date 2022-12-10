# haimtran 09 DEC 2022
# migrate ddb to opensearch serverless

import boto3
import sys
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

TABLE_NAME = ""

def index_oss(document_title, document_excerpt, document_uri):
    """
    index a document to opensearch serverless
    """
    resp = client.index(
        index="cdk-entest",
        body={
            "DocumentTitle": document_title,
            "DocumentExcerpt": document_excerpt,
            "DocumentURI": document_uri 
        },
        id=str(uuid.uuid4())
    )
    print(resp)



def scan_note():
    """
    scan all item in a table and index to oss
    """
    client = boto3.client("dynamodb")
    paginator = client.get_paginator("scan")
    #iterator
    for page in paginator.paginate(
        TableName=TABLE_NAME,
        PaginationConfig={"PageSize": 2}
    ):
        for item in page["Items"]:
            document_title = item["DocumentTitle"]["S"]
            document_excerpt = item["DocumentExcerpt"]["S"]
            document_uri = item["DocumentURI"]["S"]
            index_oss(
                document_title=document_title,
                document_uri=document_uri,
                document_excerpt=document_excerpt
            ) 



if __name__=="__main__":
    scan_note()