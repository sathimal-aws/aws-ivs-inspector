import boto3
import json

print("Getting Quotas")

serviceQuotasClient = boto3.client("service-quotas")


def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": err.message if err else res,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event["queryStringParameters"], indent=2))

    listServiceQuotasResponse = serviceQuotasClient.list_service_quotas(
        ServiceCode=event["queryStringParameters"]["serviceCode"],
        # NextToken=event["queryStringParameters"]["nextToken"],
        MaxResults=100,
    )

    print(listServiceQuotasResponse["Quotas"])

    return respond(None, json.dumps(listServiceQuotasResponse, indent=2, default=str))
