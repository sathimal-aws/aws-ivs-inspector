import json, logging, os
import boto3
import botocore.exceptions as exceptions


logger = logging.getLogger()

dynamodb = boto3.resource("dynamodb")

stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")

print("Get Session Events")


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

    domainName = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connectionId = event["requestContext"]["connectionId"]

    try:
        body = json.loads(event["body"])
        print("streamId:", body["message"]["streamId"])
        print("channelArn:", body["message"]["channelArn"])
        stream_state_events_table.update_item(
            Key={
                "streamId": body["message"]["streamId"],
                "channelArn": body["message"]["channelArn"],
            },
            UpdateExpression="set #connectionIds = list_append(if_not_exists(#connectionIds, :emptyList), :connectionId)",
            ExpressionAttributeNames={"#connectionIds": "connectionIds"},
            ExpressionAttributeValues={
                ":connectionId": [connectionId],
                ":emptyList": [],
            },
            ReturnValues="UPDATED_NEW",
        )

        streamEventDetails = stream_state_events_table.get_item(
            Key={
                "streamId": body["message"]["streamId"],
                "channelArn": body["message"]["channelArn"],
            },
        )
        print("streamEventDetails:", streamEventDetails)

        websocketClient = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{domainName}/{stage}",
        )
        response = websocketClient.post_to_connection(
            ConnectionId=connectionId,
            Data=json.dumps(streamEventDetails["Item"]["events"], default=str).encode(),
        )
        return respond(None, json.dumps(response, indent=2, default=str))

    except exceptions.ClientError as err:
        logger.error(
            "Couldn't add connectionId %s in table %s. Here's why: %s: %s",
            connectionId,
            stream_state_events_table,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
