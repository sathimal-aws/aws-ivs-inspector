import json, logging, os
import boto3
import botocore.exceptions as exceptions

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")
stream_state_events_table = dynamodb.Table(
    f"{os.environ['project_name']}-state-events"
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
    try:
        connection_id = event["requestContext"]["connectionId"]
        logger.info(f"Connection ID: {connection_id}")

        # Find the stream details associated with the connection ID
        response = stream_state_events_table.scan(
            FilterExpression="contains(connectionIds, :connectionId)",
            ExpressionAttributeValues={":connectionId": connection_id},
        )

        if response['Items']:
            stream_details = response['Items'][0]
            logger.info(f"Stream details: {stream_details}")

            # Remove the connection ID from the list
            stream_details['connectionIds'].remove(connection_id)

            # Update the DynamoDB table
            stream_state_events_table.update_item(
                Key={
                    "streamId": stream_details["streamId"],
                    "channelArn": stream_details["channelArn"],
                },
                UpdateExpression="set connectionIds = :connectionIds",
                ExpressionAttributeValues={":connectionIds": stream_details["connectionIds"]},
            )

            return respond(None, json.dumps("Connection ID deleted successfully", default=str))
        else:
            return respond(None, json.dumps("Connection ID not found in any stream", default=str))

    except exceptions.ClientError as err:
        logger.error(
            f"Error removing connectionId {connection_id} from table {stream_state_events_table.table_name}: "
            f"{err.response['Error']['Code']}: {err.response['Error']['Message']}"
        )
        return respond(err)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return respond(e)
