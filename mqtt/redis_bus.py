
import json
import logging
import redis

from django.conf import settings


logger = logging.getLogger(__name__)

REDIS_COMMAND_CHANNEL = "iocl:mqtt:commands"


class RedisBus:

    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    def publish(self, channel, message):
        return self.client.publish(channel, message)

    def subscribe(self, channel):
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)

        logger.info(
            "Subscribed to Redis channel: %s",
            channel,
        )

        return pubsub

    def close(self):
        self.client.close()


# One shared RedisBus instance per Python process.
redis_bus = RedisBus()


def publish_mqtt_command(topic, payload, qos=1):
    """
    Send an MQTT command to the running MQTT worker through Redis.
    """

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("A valid MQTT topic is required.")

    if not isinstance(payload, str):
        raise ValueError("MQTT payload must be text.")

    if qos not in (0, 1, 2):
        raise ValueError("Invalid MQTT QoS.")

    command = {
        "topic": topic,
        "payload": payload,
        "qos": qos,
    }

    try:
        return redis_bus.publish(
            REDIS_COMMAND_CHANNEL,
            json.dumps(command),
        )

    except redis.RedisError:
        logger.exception(
            "Failed to publish MQTT command to Redis. Topic: %s",
            topic,
        )
        raise
