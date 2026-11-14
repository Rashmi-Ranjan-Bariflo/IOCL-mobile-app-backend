
import logging


logger = logging.getLogger(__name__)


class MQTTSubscriber:
    def __init__(self, mqtt_client):
        self.client = mqtt_client

    def subscribe(self, topic, qos=1):
        return self.client.subscribe(
            topic=topic,
            qos=qos,
        )

    def set_message_handler(self, callback):
        self.client.set_message_callback(callback)

    @staticmethod
    def decode_message(message):
        """
        Decode the incoming MQTT payload as UTF-8 text.

        This does not assume JSON.
        """
        return message.payload.decode(
            "utf-8",
            errors="replace",
        )
