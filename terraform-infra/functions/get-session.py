import json, logging, os
import boto3

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
stream_sessions_table = dynamodb.Table(f"{os.environ['project_name']}-stream-sessions")

def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": err if err else json.dumps(res, default=str),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event["queryStringParameters"], indent=2)}")        
    try:
        streamSessionsDetails = stream_sessions_table.get_item(
            Key={
                "streamId": event["queryStringParameters"]["stream_id"],
                "channelArn": event["queryStringParameters"]["channel_arn"],
            }
        )
        # Check if item exists
        if 'Item' in streamSessionsDetails:
            return respond(None, streamSessionsDetails['Item'])
        else:
            return respond(None, {}) 
    except Exception as e:
        return respond(e) 