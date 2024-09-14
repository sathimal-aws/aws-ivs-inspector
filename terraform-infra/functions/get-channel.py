import json
import boto3

print("Getting Channel Details")
ivsClient = boto3.client("ivs")


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

    ivsGetChannelResponse = ivsClient.get_channel(
        arn=event["queryStringParameters"]["channelArn"],
    )

    return respond(None, json.dumps(ivsGetChannelResponse, indent=2, default=str))
