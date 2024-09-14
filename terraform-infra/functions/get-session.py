import json, os
import boto3

print("Get Stream Session Details")
dynamodb = boto3.resource("dynamodb")
stream_sessions_table = dynamodb.Table(f"{os.environ['project_name']}-stream-sessions")


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

    streamSessionsDetails = stream_sessions_table.get_item(
        Key={
            "streamId": event["queryStringParameters"]["stream_id"],
            "channelArn": event["queryStringParameters"]["channel_arn"],
        }
    )

    print(streamSessionsDetails)

    return respond(None, json.dumps(streamSessionsDetails, indent=2, default=str))
