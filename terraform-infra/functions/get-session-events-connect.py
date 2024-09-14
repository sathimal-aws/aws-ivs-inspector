import json

print("Get Session Events Connections")


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    data = {
        "requestId": event["requestContext"]["requestId"],
        "connectionId": event["requestContext"]["connectionId"],
    }

    print(data)

    return {"statusCode": 200, "body": json.dumps("opened!")}
