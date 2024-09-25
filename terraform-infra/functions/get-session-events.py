import json, logging, os
import boto3
import botocore.exceptions as exceptions

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")

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
        connection_id = event["requestContext"]["connectionId"]
        body = json.loads(event["body"])
        stream_id = body["message"]["streamId"]
        channel_arn = body["message"]["channelArn"]

        # Atomically add connection ID to list if it doesn't exist
        stream_state_events_table.update_item(
            Key={
                "streamId": stream_id,
                "channelArn": channel_arn,
            },
            UpdateExpression="set #connectionIds = list_append(if_not_exists(#connectionIds, :emptyList), :connectionId)",
            ExpressionAttributeNames={"#connectionIds": "connectionIds"},
            ExpressionAttributeValues={
                ":connectionId": [connection_id],
                ":emptyList": [],
            },
            ReturnValues="UPDATED_NEW",
        )

        # Retrieve and send back the current events
        stream_event_details = stream_state_events_table.get_item(
            Key={
                "streamId": stream_id,
                "channelArn": channel_arn,
            },
        )

        websocket_client = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}",
        )
        response = websocket_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(stream_event_details["Item"]["events"], default=str).encode(),
        )

        return respond(None, json.dumps(response, default=str))

    except exceptions.ClientError as err:
        logger.error(
            f"Error adding connectionId {connection_id} to table {stream_state_events_table.table_name}: "
            f"{err.response['Error']['Code']}: {err.response['Error']['Message']}"
        )
        return respond(err)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e)
