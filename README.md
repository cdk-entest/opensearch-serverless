---
title: OpenSearch Serverless
description: build a note bookmark app using opensearch
author: haimtran
publishedDate: 07/12/2022
date: 2022-12-07
---

## Introduction

[Github](https://github.com/cdk-entest/opensearch-serverless) this shows how to setup opensearch serverless to build a note bookmark application. Frontend updated later on.

- setup aws opensearch
- interact via curl
- using python sdk
- [basic dsl language](https://opensearch.org/docs/latest/opensearch/query-dsl/full-text/#match)

## Architecture

![Untitled Diagram drawio](https://user-images.githubusercontent.com/20411077/206821536-fd46f9e1-742f-4060-9d47-cbf5b72bd282.png)

[Demo Video](https://d2cvlmmg8c0xrp.cloudfront.net/opensearch_demo.mp4)

## Configure Permission

from opensearch aws console, need grant permission to user, role to access collection and index by polcies, example

```json
[
  {
    "Rules": [
      {
        "Resource": ["collection/test"],
        "Permission": ["aoss:*"],
        "ResourceType": "collection"
      },
      {
        "Resource": ["index/test/*"],
        "Permission": ["aoss:*"],
        "ResourceType": "index"
      }
    ],
    "Principal": ["arn:aws:iam::$ACCOUNT_ID:role/RoleForLambdaIndexOpenSearch"],
    "Description": "lambdaindexopensearch"
  }
]
```

## OpenSearch Client

auth and create a client

```py
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
```

create a client

```py
client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300,
)
```

## Basic Operation

create an index

```py
resp = client.indices.create(index_name)
```

delete an index

```py
resp = client.indices.delete(index=index_name)
```

index a document

```py
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
```

query data

```py
def test_query_index(query):
    """
    test query from opensearch serverless
    """
    response = client.search(
        index="cdk-entest", body={"query": {"query_string": {"query": query}}}
    )
    print(response)
```

or test another query

```py
def test_query(query_request):
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
```

delete a document given the document id

```py
client.delete(index=index_name, id=id)
```

## Troubleshooting

update boto3

```bash
python3 -m pip install boto3 --upgrade
```
