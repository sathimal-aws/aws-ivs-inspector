import json, logging, os, ast
import boto3
import botocore.exceptions as exceptions
import calendar
from time import sleep, gmtime, strftime

logger = logging.getLogger()
ivsClient = boto3.client("ivs")
lambdaClient = boto3.client("lambda")
ecsClient = boto3.client("ecs")
dynamodb = boto3.resource("dynamodb")

stream_state_events_table = dynamodb.Table(f"{os.environ['project_name']}-state-events")
stream_sessions_table = dynamodb.Table(f"{os.environ['project_name']}-stream-sessions")
live_stream_session_connection_ids_table = dynamodb.Table(
    f"{os.environ['project_name']}-live-stream-session-connection-ids"
)

now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2, default=str))
    print("Received context: " + json.dumps(context, indent=2, default=str))

    eventNameExists = (
        "event_name" in event["detail"]
        and event["detail-type"] == "IVS Stream State Change"
    )

    print("eventNameExists:", eventNameExists)

    # add or update ivsStreamStateChange DB
    if eventNameExists and event["detail"]["event_name"] == "Session Created":
        try:
            streamStateDetails = {
                "streamId": event["detail"]["stream_id"],
                "channelArn": event["resources"][0],
                "channelName": event["detail"]["channel_name"],
                "detailType": event["detail-type"],
                "events": {
                    event["id"]: {
                        "name": event["detail"]["event_name"],
                        "time": event["time"],
                    },
                },
            }

            stream_state_events_table.put_item(Item=streamStateDetails)
        except exceptions.ClientError as err:
            logger.error(
                "Couldn't add event %s in table %s. Here's why: %s: %s",
                event["detail"]["event_name"],
                stream_state_events_table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    else:
        try:
            print("detail-type: ", event["detail-type"])
            print("detail: ", json.dumps(event["detail"], indent=4))
            if event["detail-type"] == "IVS Recording State Change":
                stream_state_events_table.update_item(
                    Key={
                        "streamId": event["detail"]["stream_id"],
                        "channelArn": event["resources"][0],
                    },
                    UpdateExpression="set events.#id = :eventValues",
                    ExpressionAttributeNames={"#id": event["id"]},
                    ExpressionAttributeValues={
                        ":eventValues": {
                            "name": event["detail"]["recording_status"],
                            "recordingSessionId": event["detail"][
                                "recording_session_id"
                            ],
                            "time": event["time"],
                        }
                    },
                    ReturnValues="UPDATED_NEW",
                )
            elif event["detail-type"] == "IVS Limit Breach":
                stream_state_events_table.update_item(
                    Key={
                        "streamId": event["detail"]["stream_id"],
                        "channelArn": event["resources"][0],
                    },
                    UpdateExpression="set events.#id = :eventValues",
                    ExpressionAttributeNames={"#id": event["id"]},
                    ExpressionAttributeValues={
                        ":eventValues": {
                            "name": event["detail"]["limit"],
                            "time": event["time"],
                            "limitUnit": event["detail"]["limit_unit"],
                            "limitValue": event["detail"]["limit_value"],
                            "exceededBy": event["detail"]["exceeded_by"],
                        }
                    },
                    ReturnValues="UPDATED_NEW",
                )
            else:
                stream_state_events_table.update_item(
                    Key={
                        "streamId": event["detail"]["stream_id"],
                        "channelArn": event["resources"][0],
                    },
                    UpdateExpression="set events.#id = :eventValues",
                    ExpressionAttributeNames={"#id": event["id"]},
                    ExpressionAttributeValues={
                        ":eventValues": {
                            "name": event["detail"]["event_name"],
                            "time": event["time"],
                        }
                    },
                    ReturnValues="UPDATED_NEW",
                )
        except exceptions.ClientError as err:
            logger.error(
                "Couldn't update event %s in table %s. Here's why: %s: %s",
                json.dumps(event["detail"], indent=4),
                stream_state_events_table,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    # sending event update to client application which are connected with websocket API
    streamEventDetails = stream_state_events_table.get_item(
        Key={
            "streamId": event["detail"]["stream_id"],
            "channelArn": event["resources"][0],
        },
    )
    print("streamEventDetails:", streamEventDetails)

    if "connectionIds" in streamEventDetails["Item"]:
        liveStreamEventsWebsocket = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{os.environ['wss_get_session_events_api_id']}.execute-api.{os.environ['region']}.amazonaws.com/ivs",
        )
        connectionIds = streamEventDetails["Item"]["connectionIds"]
        for connectionId in connectionIds:
            print("Event Connection ID:", connectionId)
            response = liveStreamEventsWebsocket.post_to_connection(
                ConnectionId=connectionId,
                Data=json.dumps(
                    streamEventDetails["Item"]["events"], default=str
                ).encode(),
            )
            print(f"{connectionId} response", response)

    # sending live stream start and end update to the client application which are connected with websocket API
    if eventNameExists and (
        event["detail"]["event_name"] == "Session Created"
        or event["detail"]["event_name"] == "Session Ended"
    ):
        liveStreamSessionsWebsocket = boto3.client(
            "apigatewaymanagementapi",
            endpoint_url=f"https://{os.environ['wss_get_live_streams_api_id']}.execute-api.{os.environ['region']}.amazonaws.com/ivs",
        )

        liveStreamSessionConnectionIds = live_stream_session_connection_ids_table.scan()

        print(
            "liveStreamSessionConnectionIds:",
            liveStreamSessionConnectionIds["Items"],
        )

        for item in liveStreamSessionConnectionIds["Items"]:
            print("live Stream Connection ID:", item["connectionId"])
            response = liveStreamSessionsWebsocket.post_to_connection(
                ConnectionId=item["connectionId"],
                Data=json.dumps(
                    event,
                    default=str,
                ).encode(),
            )
            print(f"{item['connectionId']} response", response)

    # metrics to collect
    metricsToCollect = [
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

    # Run all ECS tasks that collects metrics and saves into the DynamoDB ivs-ingest-metrics table
    if eventNameExists and event["detail"]["event_name"] == "Stream Start":
        print("getting stream session details")
        ivsGetStreamSessionResponse = ivsClient.get_stream_session(
            channelArn=event["resources"][0], streamId=event["detail"]["stream_id"]
        )

        print(
            "ivsGetStreamSessionResponse: ",
            ivsGetStreamSessionResponse["streamSession"],
        )

        streamSessionsDetails = {
            "streamId": ivsGetStreamSessionResponse["streamSession"]["streamId"],
            "channelArn": ivsGetStreamSessionResponse["streamSession"]["channel"][
                "arn"
            ],
            "channel": ivsGetStreamSessionResponse["streamSession"]["channel"],
            "ingestConfiguration": ivsGetStreamSessionResponse["streamSession"][
                "ingestConfiguration"
            ],
            "recordingConfiguration": (
                ivsGetStreamSessionResponse["streamSession"]["recordingConfiguration"]
                if "recordingConfiguration"
                in ivsGetStreamSessionResponse["streamSession"]
                else None
            ),
            "startTime": calendar.timegm(
                ivsGetStreamSessionResponse["streamSession"]["startTime"].timetuple()
            ),
            "ecsTaskIds": {},
        }

        channelId = event["resources"][0].split("/")[1]
        # streamId = event["detail"]["stream_id"]

        for metric in metricsToCollect:
            print(f'invoking ECS to get {metric["name"]}')
            environmentVariables = [
                {"name": "MetricName", "value": metric["name"]},
                {"name": "ChannelId", "value": channelId},
                {"name": "StreamId", "value": event["detail"]["stream_id"]},
                {"name": "Unit", "value": metric["unit"]},
                {"name": "Statistics", "value": metric["statistics"]},
                {"name": "StartTime", "value": event["time"]},
                {"name": "EndTime", "value": now},
                {"name": "Period", "value": "10"},
                {"name": "RegionName", "value": os.environ["region"]},
                {"name": "DbTableName", "value": f"{os.environ['project_name']}-ingest-metrics"},
                {"name": "EveryNSecond", "value": "10"},
            ]

            print(
                "revision:",
                os.environ["ecs_task_definition_revision"],
            )
            print("subnet_ids: ", ast.literal_eval(os.environ["vpc_subnets"]))
            print("security_groups: ", os.environ["vpc_security_groups"])
            print("os.environ:", os.environ)

            ecsRunTaskResponse = ecsClient.run_task(
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
                            "environment": environmentVariables,
                        },
                    ],
                },
                platformVersion="1.4.0",
                propagateTags="TASK_DEFINITION",
                startedBy=now,
                taskDefinition=f"{os.environ['project_name']}-ingest-metrics-task-definition:{os.environ['ecs_task_definition_revision']}",
            )

            print(
                "ecsRunTaskResponse:",
                json.dumps(ecsRunTaskResponse["tasks"][0], indent=2, default=str),
            )

            print(
                "ecsRunTaskTaskArnResponse:",
                json.dumps(
                    ecsRunTaskResponse["tasks"][0]["taskArn"], indent=2, default=str
                ),
            )

            streamSessionsDetails["ecsTaskIds"][metric["name"]] = ecsRunTaskResponse[
                "tasks"
            ][0]["taskArn"].split("/")[2]

            print(
                "ivsGetStreamSessionResponse:",
                json.dumps(streamSessionsDetails, indent=2, default=str),
            )

        stream_sessions_table.put_item(Item=streamSessionsDetails)

    # Stop all ECS tasks that collects metrics and saves into the DynamoDB ivs-ingest-metrics table
    elif eventNameExists and event["detail"]["event_name"] == "Stream End":
        print("streamId:", event["detail"]["stream_id"])
        streamSessionsDetails = stream_sessions_table.get_item(
            Key={
                "streamId": event["detail"]["stream_id"],
                "channelArn": event["resources"][0],
            }
        )
        print("Ended:streamSessionsDetails:", streamSessionsDetails)

        sleep(30)

        for metric in metricsToCollect:
            ecsStopTaskResponse = ecsClient.stop_task(
                cluster=f"{os.environ['project_name']}-ingest-metrics-cluster",
                task=streamSessionsDetails["Item"]["ecsTaskIds"][metric["name"]],
                reason=f'Session with ID: {event["detail"]["stream_id"]} ended',
            )

            ecsTaskLastStatus = ecsStopTaskResponse["task"]["lastStatus"]
            ecsTaskDesiredStatus = ecsStopTaskResponse["task"]["desiredStatus"]

            print("ecsTaskLastStatus:", ecsTaskLastStatus)
            print("ecsTaskDesiredStatus:", ecsTaskDesiredStatus)

    return {"statusCode": 200, "body": json.dumps("metrics initiated successfully")}
