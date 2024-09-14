import boto3
import json

print("List Stream Sessions")
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

    ivsListStreamSessionResponse = ivsClient.list_stream_sessions(
        channelArn=event["queryStringParameters"]["channelArn"],
        nextToken=event["queryStringParameters"]["nextToken"],
        maxResults=100,
    )

    print(ivsListStreamSessionResponse)

    return respond(
        None, json.dumps(ivsListStreamSessionResponse, indent=2, default=str)
    )
