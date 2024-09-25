import logging, os
import boto3
import botocore.exceptions as exceptions

print("Getting Live Stream Disconnections")

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
    connectionId = event["requestContext"]["connectionId"]
    try:
        live_stream_session_connection_ids_table.delete_item(
            Key={
                "connectionId": connectionId,
            },
        )

        return respond(None, "connection ID deleted!")

    except exceptions.ClientError as err:
        logger.error(
            "Couldn't add connectionId %s in table %s. Here's why: %s: %s",
            connectionId,
            live_stream_session_connection_ids_table,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
