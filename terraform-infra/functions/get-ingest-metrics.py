import json, os
import boto3

print("Loading function")

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

    # if (
    #     event["Records"][0]["eventName"] == "INSERT"
    #     or event["Records"][0]["eventName"] == "MODIFY"
    # ):
    #     new_data = json.dumps(event["Records"][0]["dynamodb"]["NewImage"])

    #     print(new_data)

    #     streamId = new_data["streamId"]["S"]
    #     channelId = new_data["channelId"]["S"]

    #     streamEventDetails = stream_state_events_table.get_item(
    #         Key={
    #             "streamId": streamId,
    #             "channelArn": f"arn:aws:ivs:us-west-2:740024244647:channel/{channelId}",
    #         },
    #     )
    #     print("Ended:streamEventDetails:", streamEventDetails)

    #     if "connectionIds" in streamEventDetails["Item"]:
    #         liveStreamEventsWebsocket = boto3.client(
    #             "apigatewaymanagementapi",
    #             endpoint_url=f"https://{os.environ["wss_api_id"]}.execute-api.{os.environ["region"]}.amazonaws.com/ivs",
    #         )
    #         connectionIds = streamEventDetails["Item"]["connectionIds"]
    #         for connectionId in connectionIds:
    #             print("Event Connection ID:", connectionId)
    #             response = liveStreamEventsWebsocket.post_to_connection(
    #                 ConnectionId=connectionId,
    #                 Data=json.dumps(
    #                     streamEventDetails["Item"]["events"], default=str
    #                 ).encode(),
    #             )
    #             print(f"{connectionId} response", response)

    data = ingest_metrics_table.get_item(
        Key={
            "streamId": event["queryStringParameters"]["stream_id"],
            "channelId": event["queryStringParameters"]["channel_id"],
        }
    )

    print(json.dumps(data, indent=2, default=str))
    if data["Item"]:
        return respond(None, json.dumps(data["Item"], indent=2, default=str))
