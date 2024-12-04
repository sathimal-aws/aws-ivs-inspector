import json, logging, os
import boto3
import botocore.exceptions

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
live_stream_session_connection_ids_table = dynamodb.Table(
    f"{os.environ['project_name']}-live-stream-session-connection-ids"
)

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
    connection_id = event["requestContext"]["connectionId"]

    try:
        live_stream_session_connection_ids_table.put_item(
            Item={
                "connectionId": connection_id,
            }
        )

        logger.info(f"Connection ID {connection_id} added successfully.")
        return respond(None, json.dumps(f"Connection ID {connection_id} added successfully.", default=str))

    except botocore.exceptions.ClientError as err:
        logger.error(
            f"Couldn't add connectionId {connection_id} to table {live_stream_session_connection_ids_table.table_name}. "
            f"Error: {err.response['Error']['Code']}: {err.response['Error']['Message']}"
        )
        return respond(err)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e)
