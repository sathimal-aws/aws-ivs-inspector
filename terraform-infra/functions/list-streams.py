import json, logging
import boto3

logger = logging.getLogger()
ivsClient = boto3.client("ivs")

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
    logger.info(f"Received event: {json.dumps(event["queryStringParameters"], indent=2)}")        
    try:
        nextToken = event["queryStringParameters"].get("nextToken")
        ivsListStreamsResponse = ivsClient.list_streams(
            nextToken=nextToken if nextToken else None,
            maxResults=100,
        )

        return respond(None, ivsListStreamsResponse)
    except Exception as e:
        return respond(e)
