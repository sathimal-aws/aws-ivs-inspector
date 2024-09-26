import json, logging, os
import boto3

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
ingest_metrics_table = dynamodb.Table(f"{os.environ['project_name']}-ingest-metrics")


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
        data = ingest_metrics_table.get_item(
            Key={
                "streamId": event["queryStringParameters"]["stream_id"],
                "channelId": event["queryStringParameters"]["channel_id"],
            }
        )

        if "Item" in data:
            logger.info(f"Retrieved ingest metrics: {json.dumps(data['Item'], indent=2, default=str)}")
            return respond(None, json.dumps(data['Item'], default=str))
        else:
            logger.info(f"No ingest metrics found for stream ID: {event['queryStringParameters']['stream_id']} and channel ID: {event['queryStringParameters']['channel_id']}")
            return respond(None, json.dumps({}, default=str))  # Return an empty dictionary if no item is found

    except Exception as e:
        logger.error(f"Error fetching ingest metrics: {str(e)}")
        return respond(json.dumps(e, default=str))
