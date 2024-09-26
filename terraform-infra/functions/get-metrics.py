import json, logging
import boto3
from datetime import datetime, timedelta

logger = logging.getLogger()

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
        cloudwatch_client = boto3.client(
            "cloudwatch", region_name=event["queryStringParameters"]["regionName"]
        )

        metrics_to_collect = [
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
        for metric in metrics_to_collect:
            response = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/IVS",
                MetricName=metric["name"],
                StartTime=datetime.now() - timedelta(hours=24),
                EndTime=datetime.now(),
                Period=metric["period"],
                Statistics=metric["statistics"],
                Unit=metric["unit"],
            )
            metrics.append(response)

        return respond(None, json.dumps(metrics, default=str))

    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return respond(e)
