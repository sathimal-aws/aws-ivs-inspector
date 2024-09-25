import ast
import os
import boto3
import json
import botocore.exceptions as exceptions 
import logging
from time import sleep
from datetime import datetime, timedelta

from decimal import Decimal

logger = logging.getLogger()

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event):
    print("Received event json: " + json.dumps(event, indent=2, default=str))
    ingestLogsTable = dynamodb.Table(event["DbTableName"])
    cloudWatchClient = boto3.client("cloudwatch", region_name=event["RegionName"])

    isStreamLive = True

    startTime = event["StartTime"]

    try:
        print("MetricName:", event["MetricName"])
        ingestLogsTable.update_item(
            Key={
                "streamId": event["StreamId"],
                "channelId": event["ChannelId"],
            },
            UpdateExpression="set #metricName = :value",
            ConditionExpression="attribute_not_exists(#metricName)",
            ExpressionAttributeNames={
                "#metricName": event["MetricName"],
            },
            ExpressionAttributeValues={":value": {}},
            ReturnValues="UPDATED_NEW",
        )
        while isStreamLive:
            metrics = cloudWatchClient.get_metric_statistics(
                Namespace="AWS/IVS",
                MetricName=event["MetricName"],
                Dimensions=[
                    {"Name": "Channel", "Value": event["ChannelId"]},
                ],
                StartTime=startTime,
                EndTime=datetime.now(),
                Period=int(event["Period"]),
                Statistics=ast.literal_eval(event["Statistics"]),
                Unit=event["Unit"],
            )

            print('metrics["Datapoints"]:', metrics["Datapoints"])

            if len(metrics["Datapoints"]) > 0:
                sortedDate = sorted(
                    metrics["Datapoints"], key=lambda x: x["Timestamp"], reverse=True
                )
                startTime = sortedDate[0]["Timestamp"] - timedelta(minutes=1)

                for data in sortedDate:
                    ingestLogsTable.update_item(
                        Key={
                            "streamId": event["StreamId"],
                            "channelId": event["ChannelId"],
                        },
                        UpdateExpression="set #metricName.#eventTime = :metricValues",
                        ExpressionAttributeNames={
                            "#metricName": event["MetricName"],
                            "#eventTime": str(
                                int(datetime.timestamp(data["Timestamp"]))
                            ),
                        },
                        ExpressionAttributeValues={
                            ":metricValues": round(Decimal(f'{data["Average"]}'), 3),
                        },
                        ReturnValues="UPDATED_NEW",
                    )
            sleep(int(event["EveryNSecond"]))

    except exceptions.ClientError as err:
        logger.error(
            "Couldn't add metric %s in table %s. Here's why: %s: %s",
            event["MetricName"],
            ingestLogsTable,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

    return {
        "statusCode": 200,
    }


lambda_handler(os.environ)
