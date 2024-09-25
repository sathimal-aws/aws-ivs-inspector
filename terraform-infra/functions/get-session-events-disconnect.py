import json, logging, os
import boto3
import botocore.exceptions as exceptions

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
from boto3.dynamodb.conditions import Key, Attr

print("Get Session Events Disconnections")


stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")


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
    try:
        connectionId = event["requestContext"]["connectionId"]
        print("connectionId:", connectionId)

        data = stream_state_events_table.scan(
            FilterExpression=Attr("connectionIds").contains(connectionId)
        )

        streamDetails = data["Items"][0]

        print("streamDetails:", streamDetails)

        if "connectionIds" in streamDetails:
            print("connectionIds before: ", streamDetails["connectionIds"])
            streamDetails["connectionIds"].remove(connectionId)
            print("connectionIds after: ", streamDetails["connectionIds"])
            stream_state_events_table.update_item(
                Key={
                    "streamId": streamDetails["streamId"],
                    "channelArn": streamDetails["channelArn"],
                },
                UpdateExpression="set #connectionIds =:connectionIds",
                ExpressionAttributeNames={"#connectionIds": "connectionIds"},
                ExpressionAttributeValues={
                    ":connectionIds": streamDetails["connectionIds"],
                },
                ReturnValues="UPDATED_NEW",
            )

            return respond(None, "connection ID deleted!")

    except exceptions.ClientError as err:
        logger.error(
            "Couldn't add connectionId %s in table %s. Here's why: %s: %s",
            connectionId,
            stream_state_events_table,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
