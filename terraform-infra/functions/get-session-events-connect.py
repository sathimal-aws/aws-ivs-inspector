import json, logging

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
        # It's good practice to log the connection ID for debugging
        connection_id = event["requestContext"]["connectionId"]
        logger.info(f"Connection ID: {connection_id} connected.")

        return respond(None, json.dumps("Connection established successfully!", default=str))

    except Exception as e:
        logger.error(f"Error establishing connection: {str(e)}")
        return respond(e)
