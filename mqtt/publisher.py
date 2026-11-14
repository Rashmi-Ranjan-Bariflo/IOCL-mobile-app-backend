
import logging


logger = logging.getLogger(__name__)


class MQTTPublisher:
    def __init__(self, mqtt_client):
        self.client = mqtt_client

    def publish(self, topic, payload, qos=1, retain=False):
        try:
            return self.client.publish(
                topic=topic,
                payload=payload,
                qos=qos,
                retain=retain,
            )

        except Exception:
            logger.exception(
                "Failed to publish MQTT message to topic: %s",
                topic,
            )
            raise
