import localstack_client.session as boto3
import pytest

from tests.test_config import config


@pytest.fixture
def sqs_client():
    return boto3.client("sqs")


def test_sqs_queue_url_exists(config, sqs_client):
    assert (
        sqs_client.get_queue_url(QueueName="login-queue")["QueueUrl"]
        == config["DEV"]["queue_url"]
    )
