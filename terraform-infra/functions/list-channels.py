import json, logging
import boto3

logger = logging.getLogger()
ivsClient = boto3.client("ivs")

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
        ivsGetChannelsResponse = ivsClient.list_channels(
            nextToken=nextToken if nextToken else "",
            maxResults=100,
        )

        return respond(None, json.dumps(ivsGetChannelsResponse, default=str))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e)