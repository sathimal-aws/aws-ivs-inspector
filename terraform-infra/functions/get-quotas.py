import json, logging
import boto3

logger = logging.getLogger()
serviceQuotasClient = boto3.client("service-quotas")


def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": err if err else res,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event, indent=2)}")
    try:
        nextToken = event["queryStringParameters"].get("nextToken")
        listServiceQuotasResponse = serviceQuotasClient.list_service_quotas(
            ServiceCode=event["queryStringParameters"]["serviceCode"],
            NextToken=nextToken if nextToken else "",
            MaxResults=100,
        )

        print("listServiceQuotasResponse:", listServiceQuotasResponse)

        return respond(None, json.dumps(listServiceQuotasResponse, default=str))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e)
    
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event["queryStringParameters"], indent=2))

    listServiceQuotasResponse = serviceQuotasClient.list_service_quotas(
        ServiceCode=event["queryStringParameters"]["serviceCode"],
        # NextToken=event["queryStringParameters"]["nextToken"],
        MaxResults=100,
    )

    return respond(None, json.dumps(listServiceQuotasResponse, indent=2, default=str))
