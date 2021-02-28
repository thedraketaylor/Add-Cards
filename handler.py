import json
import boto3
import logging
from os import environ
from botocore.exceptions import ClientError


def get_queue_url(sqs, name):
    response = sqs.get_queue_url(QueueName=name)
    return response["QueueUrl"], response["ResponseMetadata"]["HTTPStatusCode"]


def return_object(status, message):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(message),
    }


def add_card_to_sqs(sqs, queue_url, card):
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=card,
    )
    return return_object(200, "Card was added Successfully")


def add_card(event, context):
    sqs = boto3.client("sqs")
    if "body" not in event or not isinstance(event["body"], str):
        raise KeyError("body")
    card = event["body"]
    queue_url, status = get_queue_url(sqs, environ["queue_name"])
    if status != 200:
        logging.error(queue_url)
        return return_object(status, queue_url)
    return add_card_to_sqs(sqs, queue_url, card)
