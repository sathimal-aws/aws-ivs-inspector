import json, logging
import boto3
from datetime import datetime, timedelta

logger = logging.getLogger()

def respond(err, res=None):
    return {
        "statusCode": 400 if err else 200,
        "body": json.dumps({"message": err.message}) if err else json.dumps({"message": res}),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event["queryStringParameters"], indent=2))

    cloudWatchClient = boto3.client(
        "cloudwatch", region_name=event["queryStringParameters"]["regionName"]
    )

    # metrics to collect
    metricsToCollect = [
        {
            "name": "ConcurrentViews",
            "unit": "Count",
            "statistics": ["Average", "Maximum", "Minimum"],
            "period": 120,
        },
        {
            "name": "ConcurrentStreams",
            "unit": "Count",
            "statistics": ["Average", "Maximum", "Minimum"],
            "period": 120,
        },
        {
            "name": "LiveDeliveredTime",
            "unit": "Seconds",
            "statistics": ["Sum"],
            "period": 300,
        },
        {
            "name": "LiveInputTime",
            "unit": "Seconds",
            "statistics": ["Sum"],
            "period": 300,
        },
        {
            "name": "RecordedTime",
            "unit": "Seconds",
            "statistics": ["Sum"],
            "period": 300,
        },
    ]

    metrics = []

    for metric in metricsToCollect:
        metrics.append(
            cloudWatchClient.get_metric_statistics(
                Namespace="AWS/IVS",
                MetricName=metric["name"],
                StartTime=datetime.now() - timedelta(hours=24),
                EndTime=datetime.now(),
                Period=metric["period"],
                Statistics=metric["statistics"],
                Unit=metric["unit"],
            )
        )

    print(metrics)

    return respond(None, json.dumps(metrics, indent=2, default=str))
