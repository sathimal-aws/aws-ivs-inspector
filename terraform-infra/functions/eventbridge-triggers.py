import json, logging, os, ast, calendar
from time import sleep, gmtime, strftime

import boto3
import botocore.exceptions

logger = logging.getLogger()
ivs_client = boto3.client("ivs")
lambda_client = boto3.client("lambda")
ecs_client = boto3.client("ecs")
dynamodb = boto3.resource("dynamodb")

stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")
stream_sessions_table = dynamodb.Table(f"{os.environ['project_name']}-stream-sessions")
live_stream_session_connection_ids_table = dynamodb.Table(
    f"{os.environ['project_name']}-live-stream-session-connection-ids"
)

now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

METRICS_TO_COLLECT = [
    {
        "name": "IngestVideoBitrate",
        "unit": "Bits/Second",
        "statistics": '["Average", "Maximum", "Minimum"]',
    },
    {
        "name": "IngestAudioBitrate",
        "unit": "Bits/Second",
        "statistics": '["Average", "Maximum", "Minimum"]',
    },
    {
        "name": "IngestFramerate",
        "unit": "Count/Second",
        "statistics": '["Average", "Maximum", "Minimum"]',
    },
    {
        "name": "KeyframeInterval",
        "unit": "Seconds",
        "statistics": '["Average", "Maximum", "Minimum"]',
    },
    {
        "name": "ConcurrentViews",
        "unit": "Count",
        "statistics": '["Average", "Maximum", "Minimum"]',
    },
]

def update_stream_state_events(event):
    """Updates the stream state events table with the given event."""
    detail_type = event["detail-type"]
    detail = event["detail"]
    event_id = event["id"]
    stream_id = detail["stream_id"]
    channel_arn = event["resources"][0]

    try:
        if detail_type == "IVS Recording State Change":
            stream_state_events_table.update_item(
                Key={"streamId": stream_id, "channelArn": channel_arn},
                UpdateExpression="set events.#id = :eventValues",
                ExpressionAttributeNames={"#id": event_id},
                ExpressionAttributeValues={
                    ":eventValues": {
                        "name": detail["recording_status"],
                        "recordingSessionId": detail.get("recording_session_id"),
                        "time": event["time"],
                    }
                },
                ReturnValues="UPDATED_NEW",
            )
        elif detail_type == "IVS Limit Breach":
            stream_state_events_table.update_item(
                Key={"streamId": stream_id, "channelArn": channel_arn},
                UpdateExpression="set events.#id = :eventValues",
                ExpressionAttributeNames={"#id": event_id},
                ExpressionAttributeValues={
                    ":eventValues": {
                        "name": detail["limit"],
                        "time": event["time"],
                        "limitUnit": detail["limit_unit"],
                        "limitValue": detail["limit_value"],
                        "exceededBy": detail["exceeded_by"],
                    }
                },
                ReturnValues="UPDATED_NEW",
            )
        else:
            stream_state_events_table.update_item(
                Key={"streamId": stream_id, "channelArn": channel_arn},
                UpdateExpression="set events.#id = :eventValues",
                ExpressionAttributeNames={"#id": event_id},
                ExpressionAttributeValues={
                    ":eventValues": {"name": detail["event_name"], "time": event["time"]}
                },
                ReturnValues="UPDATED_NEW",
            )
    except botocore.exceptions.ClientError as err:
        logger.error(
            "Couldn't update event %s in table %s. Error: %s: %s",
            json.dumps(event["detail"], indent=4),
            stream_state_events_table.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

def send_websocket_updates(event):
    """Sends WebSocket updates to connected clients."""
    stream_id = event["detail"]["stream_id"]
    channel_arn = event["resources"][0]

    # Send event update to clients connected to the session events WebSocket API
    stream_event_details = stream_state_events_table.get_item(
        Key={"streamId": stream_id, "channelArn": channel_arn}
    )
    if "Item" in stream_event_details and "connectionIds" in stream_event_details["Item"]:
        live_stream_events_websocket = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{os.environ['wss_get_session_events_api_id']}.execute-api.{os.environ['region']}.amazonaws.com/ivs",
        )
        for connection_id in stream_event_details["Item"]["connectionIds"]:
            try:
                live_stream_events_websocket.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps(stream_event_details["Item"]["events"], default=str).encode(),
                )
            except botocore.exceptions.ClientError as err:
                logger.error(f"Error sending to connection {connection_id}: {err}")

    # Send live stream start/end updates to clients connected to the live streams WebSocket API
    event_name = event["detail"]["event_name"]
    if event_name in ("Session Created", "Session Ended"):
        live_stream_sessions_websocket = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{os.environ['wss_get_live_streams_api_id']}.execute-api.{os.environ['region']}.amazonaws.com/ivs",
        )
        live_stream_session_connections = live_stream_session_connection_ids_table.scan()
        for item in live_stream_session_connections.get("Items", []):
            try:
                live_stream_sessions_websocket.post_to_connection(
                    ConnectionId=item["connectionId"],
                    Data=json.dumps(event, default=str).encode(),
                )
            except botocore.exceptions.ClientError as err:
                logger.error(f"Error sending to connection {item['connectionId']}: {err}")

def start_ingest_metrics_collection(event):
    """Starts ECS tasks to collect ingest metrics."""
    stream_id = event["detail"]["stream_id"]
    channel_arn = event["resources"][0]
    channel_id = channel_arn.split("/")[1]

    try:
        ivs_get_stream_session_response = ivs_client.get_stream_session(
            channelArn=channel_arn, streamId=stream_id
        )
        stream_session = ivs_get_stream_session_response["streamSession"]

        stream_session_details = {
            "streamId": stream_session["streamId"],
            "channelArn": stream_session["channel"]["arn"],
            "channel": stream_session["channel"],
            "ingestConfiguration": stream_session["ingestConfiguration"],
            "recordingConfiguration": stream_session.get("recordingConfiguration"),
            "startTime": calendar.timegm(stream_session["startTime"].timetuple()),
            "ecsTaskIds": {},
        }

        for metric in METRICS_TO_COLLECT:
            environment_variables = [
                {"name": "MetricName", "value": metric["name"]},
                {"name": "ChannelId", "value": channel_id},
                {"name": "StreamId", "value": stream_id},
                {"name": "Unit", "value": metric["unit"]},
                {"name": "Statistics", "value": metric["statistics"]},
                {"name": "StartTime", "value": event["time"]},
                {"name": "EndTime", "value": now},
                {"name": "Period", "value": "10"},
                {"name": "RegionName", "value": os.environ["region"]},
                {"name": "DbTableName", "value": f"{os.environ['project_name']}-ingest-metrics"},
                {"name": "EveryNSecond", "value": "10"},
            ]

            ecs_run_task_response = ecs_client.run_task(
                cluster=f"{os.environ['project_name']}-ingest-metrics-cluster",
                count=1,
                enableECSManagedTags=True,
                enableExecuteCommand=True,
                group=f"family:{os.environ['project_name']}-ingest-metrics-task-definition:{os.environ['ecs_task_definition_revision']}",
                launchType="FARGATE",
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "securityGroups": [os.environ["vpc_security_groups"]],
                        "subnets": ast.literal_eval(os.environ["vpc_subnets"]),
                    }
                },
                overrides={
                    "containerOverrides": [
                        {
                            "name": f"{os.environ['project_name']}-ingest-metrics-container",
                            "environment": environment_variables,
                        },
                    ],
                },
                platformVersion="1.4.0",
                propagateTags="TASK_DEFINITION",
                startedBy=now,
                taskDefinition=f"{os.environ['project_name']}-ingest-metrics-task-definition:{os.environ['ecs_task_definition_revision']}",
            )

            task_arn = ecs_run_task_response["tasks"][0]["taskArn"].split("/")[2]
            stream_session_details["ecsTaskIds"][metric["name"]] = task_arn

        stream_sessions_table.put_item(Item=stream_session_details)

    except (botocore.exceptions.ClientError, KeyError) as err:
        logger.error(f"Error starting ingest metrics collection: {err}")

def add_stream_end_time(event):
    """Adds the stream end time to the stream sessions table."""
    stream_id = event["detail"]["stream_id"]
    channel_arn = event["resources"][0]

    try:
        ivs_get_stream_session_response = ivs_client.get_stream_session(
            channelArn=channel_arn, streamId=stream_id
        )
        stream_session_end_time = calendar.timegm(ivs_get_stream_session_response["streamSession"]["endTime"].timetuple())

        if "streamSession" in ivs_get_stream_session_response:
            stream_sessions_table.update_item(
                Key={"streamId": stream_id, "channelArn": channel_arn},
                UpdateExpression="set endTime = :endTime",
                ExpressionAttributeValues={":endTime": stream_session_end_time},
                ReturnValues="UPDATED_NEW",
            )
    except (botocore.exceptions.ClientError, KeyError) as err:
        logger.error(f"Error adding stream end time: {err}")

def stop_ingest_metrics_collection(event):
    """Stops ECS tasks that are collecting ingest metrics."""
    stream_id = event["detail"]["stream_id"]
    channel_arn = event["resources"][0]

    try:
        stream_session_details = stream_sessions_table.get_item(
            Key={"streamId": stream_id, "channelArn": channel_arn}
        )

        sleep(30)  # Wait for a short period to allow metrics collection to finish

        for metric_name, task_id in stream_session_details["Item"]["ecsTaskIds"].items():
            ecs_client.stop_task(
                cluster=f"{os.environ['project_name']}-ingest-metrics-cluster",
                task=task_id,
                reason=f"Session with ID: {stream_id} ended",
            )

    except (botocore.exceptions.ClientError, KeyError) as err:
        logger.error(f"Error stopping ingest metrics collection: {err}")

def lambda_handler(event, context):
    """Handles EventBridge events related to IVS streams."""
    logger.info(f"Received event: {json.dumps(event, indent=2)}")

    event_name = event["detail"].get("event_name")
    is_stream_state_change = event["detail-type"] == "IVS Stream State Change"

    try:
        if is_stream_state_change:
            if event_name == "Session Created":
                stream_state_details = {
                    "streamId": event["detail"]["stream_id"],
                    "channelArn": event["resources"][0],
                    "channelName": event["detail"]["channel_name"],
                    "detailType": event["detail-type"],
                    "events": {
                        event["id"]: {"name": event_name, "time": event["time"]},
                    },
                }
                stream_state_events_table.put_item(Item=stream_state_details)
            else:
                update_stream_state_events(event)

            send_websocket_updates(event)

        if is_stream_state_change and event_name == "Stream Start":
            start_ingest_metrics_collection(event)
        elif is_stream_state_change and event_name == "Stream End":
            add_stream_end_time(event)
            stop_ingest_metrics_collection(event)

        return {"statusCode": 200, "body": json.dumps("Event processed successfully")}

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error processing event: {str(e)}")}
