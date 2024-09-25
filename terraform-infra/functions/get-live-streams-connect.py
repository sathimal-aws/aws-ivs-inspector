import json, logging, os
import boto3
import botocore.exceptions as exceptions

print("Getting Live Stream Connections")

logger = logging.getLogger()

dynamodb = boto3.resource("dynamodb")

live_stream_session_connection_ids_table = dynamodb.Table(
    f"{os.environ['project_name']}-live-stream-session-connection-ids"
)


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
    print("Received event: " + json.dumps(event, indent=2))
    eventType = event["requestContext"]["eventType"]
    connectionId = event["requestContext"]["connectionId"]

    print("eventType:", eventType)

    try:
        print("connectionId:", connectionId)
        live_stream_session_connection_ids_table.put_item(
            Item={
                "connectionId": connectionId,
            }
        )

        return respond(None, "connection ID added!")

    except exceptions.ClientError as err:
        logger.error(
            "Couldn't add connectionId %s in table %s. Here's why: %s: %s",
            connectionId,
            live_stream_session_connection_ids_table,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
