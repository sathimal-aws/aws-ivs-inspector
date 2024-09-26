import json, logging
from time import sleep
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
        sleep(3) # adding delay to the call
        ivsGetStreamResponse = ivsClient.get_stream(
            channelArn=event["queryStringParameters"]["channelArn"],
        )

        logger.info(f"get stream response: {json.dumps(ivsGetStreamResponse, indent=2, default=str)}")        
        return respond(None, json.dumps(ivsGetStreamResponse, default=str))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(json.dumps(e, default=str))
