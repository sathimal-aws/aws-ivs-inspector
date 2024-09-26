import json, logging, os
import boto3

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
stream_sessions_table = dynamodb.Table(f"{os.environ['project_name']}-stream-sessions")

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
        data = stream_sessions_table.get_item(
            Key={
                "streamId": event["queryStringParameters"]["stream_id"],
                "channelArn": event["queryStringParameters"]["channel_arn"],
            }
        )
        # Check if item exists
        if "Item" in data:
            logger.info(f"Retrieved stream session: {json.dumps(data['Item'], indent=2, default=str)}")
            return respond(None, json.dumps(data['Item'], default=str))
        else:
            print(f"No stream session found for stream ID: {event['queryStringParameters']['stream_id']}")
            logger.info(f"No stream session found for stream ID: {event['queryStringParameters']['stream_id']}")
            return respond(None, json.dumps({}, default=str))  # Return an empty dictionary if no item is found

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e) 