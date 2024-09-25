import json, logging
import boto3

logger = logging.getLogger()
ivsClient = boto3.client("ivs")

def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": json.dumps({"message": err.message}) if err else json.dumps({"message": res}),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event["queryStringParameters"], indent=2)}")        
    try:
        ivsGetStreamResponse = ivsClient.get_stream(
            channelArn=event["queryStringParameters"]["channelArn"],
        )

        return respond(None, ivsGetStreamResponse)
    except Exception as e:
        return respond(e)