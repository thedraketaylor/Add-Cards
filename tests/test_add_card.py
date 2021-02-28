import sys
import mock
import boto3
import json
import botocore
import pytest
import copy

sys.path.append("../")
from os import environ

from moto import mock_sqs
import handler

import botocore.exceptions

return_obj = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    },
    "body": json.dumps("message"),
}

card_val = {"front": "front", "back": "back"}

card = json.dumps(card_val)


@mock_sqs
def test_queue_url_good_queue():
    sqs = boto3.client("sqs")
    sqs.create_queue(QueueName="test")
    _, status = handler.get_queue_url(sqs, "test")
    assert status == 200


def test_return_object():
    status = 200
    body = "message"
    r = handler.return_object(status, body)
    assert r == return_obj


@mock_sqs
def test_add_card():
    sqs = boto3.client("sqs")
    l = sqs.create_queue(QueueName="test")
    h = handler.add_card_to_sqs(sqs, l["QueueUrl"], card)
    obj = copy.deepcopy(return_obj)
    obj["body"] = json.dumps("Card was added Successfully")
    assert h == obj


def test_add_card_good(monkeypatch):
    def test_get_queue_url(sqs, queue):
        return "queue_url", 200

    def test_add_card_sqs(sqs, url, card):
        return return_obj

    monkeypatch.setenv("queue_name", "test")
    monkeypatch.setattr(handler, "get_queue_url", test_get_queue_url)
    monkeypatch.setattr(handler, "add_card_to_sqs", test_add_card_sqs)
    event = {"body": "card stuff"}
    response = handler.add_card(event, "context")
    assert response["statusCode"] == 200


def test_add_card_bad(monkeypatch):
    def test_get_queue_url(sqs, queue):
        return "queue_url", 404

    monkeypatch.setenv("queue_name", "test")
    monkeypatch.setattr(handler, "get_queue_url", test_get_queue_url)
    event = {"body": "card stuff"}
    response = handler.add_card(event, "context")
    assert response["statusCode"] == 404


def test_add_card_missing(monkeypatch):
    with pytest.raises(KeyError):
        monkeypatch.setenv("queue_name", "test")
        event = {}
        handler.add_card(event, "context")
