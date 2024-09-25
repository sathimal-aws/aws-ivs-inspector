import json, logging
import boto3

logger = logging.getLogger()
serviceQuotasClient = boto3.client("service-quotas")


def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": err.message if err else json.dumps(res, default=str),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event['queryStringParameters'], indent=2)}")
    try:
        nextToken = event["queryStringParameters"].get("nextToken")
        listServiceQuotasResponse = serviceQuotasClient.list_service_quotas(
            ServiceCode=event["queryStringParameters"]["serviceCode"],
            nextToken=nextToken if nextToken else None,
            MaxResults=100,
        )

        return respond(None, listServiceQuotasResponse)
    except Exception as e:
        return respond(e)