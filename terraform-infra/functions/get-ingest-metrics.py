import json, os
import boto3

print("Getting Ingest Metrics")

dynamodb = boto3.resource("dynamodb")
ivsClient = boto3.client("ivs")
stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")
ingest_metrics_table = dynamodb.Table(f"{os.environ['project_name']}-ingest-metrics")


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
    data = ingest_metrics_table.get_item(
        Key={
            "streamId": event["queryStringParameters"]["stream_id"],
            "channelId": event["queryStringParameters"]["channel_id"],
        }
    )

    print(json.dumps(data, indent=2, default=str))
    if data["Item"]:
        return respond(None, json.dumps(data["Item"], indent=2, default=str))
