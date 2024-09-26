import ast, json, logging, os
from datetime import datetime, timedelta
from time import sleep
import boto3
import botocore.exceptions
from decimal import Decimal

logger = logging.getLogger()
dynamodb = boto3.resource("dynamodb")


def main(event):
    """Collects and stores ingest metrics from CloudWatch to DynamoDB."""

    logger.info(f"Received event: {json.dumps(event, indent=2, default=str)}")
    ingest_logs_table = dynamodb.Table(event["DbTableName"])
    cloudwatch_client = boto3.client("cloudwatch", region_name=event["RegionName"])

    start_time = event["StartTime"]

    try:
        # Create the metric entry in DynamoDB if it doesn't exist
        ingest_logs_table.update_item(
            Key={"streamId": event["StreamId"], "channelId": event["ChannelId"]},
            UpdateExpression="set #metricName = :value",
            ConditionExpression="attribute_not_exists(#metricName)",
            ExpressionAttributeNames={"#metricName": event["MetricName"]},
            ExpressionAttributeValues={":value": {}},
            ReturnValues="UPDATED_NEW",        
            )

        while True:  # Run indefinitely until the function is stopped or an error occurs
            metrics = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/IVS",
                MetricName=event["MetricName"],
                Dimensions=[{"Name": "Channel", "Value": event["ChannelId"]}],
                StartTime=start_time,
                EndTime=datetime.now(),
                Period=int(event["Period"]),
                Statistics=ast.literal_eval(event["Statistics"]),
                Unit=event["Unit"],
            )

            logger.debug(f'metrics["Datapoints"]: {metrics["Datapoints"]}')

            if metrics["Datapoints"]:
                # Sort datapoints by timestamp in descending order
                sorted_data = sorted(
                    metrics["Datapoints"], key=lambda x: x["Timestamp"], reverse=True
                )
                # Update start_time for the next iteration
                start_time = sorted_data[0]["Timestamp"] - timedelta(minutes=1)

                for datapoint in sorted_data:
                    event_time = str(int(datetime.timestamp(datapoint["Timestamp"])))
                    ingest_logs_table.update_item(
                        Key={"streamId": event["StreamId"], "channelId": event["ChannelId"]},
                        UpdateExpression="set #metricName.#eventTime = :metricValue",
                        ExpressionAttributeNames={
                            "#metricName": event["MetricName"],
                            "#eventTime": event_time,
                        },
                        ExpressionAttributeValues={
                            ":metricValue": round(Decimal(datapoint["Average"]), 3)
                        },
                    )

            sleep(int(event["EveryNSecond"]))

    except botocore.exceptions.ClientError as err:
        logger.error(
            "Couldn't add metric %s to table %s. Error: %s: %s",
            event["MetricName"],
            ingest_logs_table.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise  # Re-raise the exception to stop the function execution

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise  # Re-raise the exception to stop the function execution

if __name__ == "__main__":
    main(os.environ)
