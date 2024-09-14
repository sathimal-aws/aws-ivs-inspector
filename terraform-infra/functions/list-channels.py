import boto3
import json

print("Getting List of Channels")

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

    ivsGetChannelsResponse = ivsClient.list_channels(
        maxResults=6,
        nextToken=event["queryStringParameters"]["nextToken"],
    )

    print("Response: " + json.dumps(ivsGetChannelsResponse, indent=2))

    return respond(None, json.dumps(ivsGetChannelsResponse, indent=2, default=str))
