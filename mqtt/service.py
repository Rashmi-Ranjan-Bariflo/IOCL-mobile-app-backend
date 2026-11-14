
import logging

from .client import MQTTClient
from .publisher import MQTTPublisher
from .subscriber import MQTTSubscriber
from .topics import (
    MQTT_VALVE_ACK_TOPIC,
    MQTT_VALVE_STATUS_TOPIC,
    MQTT_SUBSCRIPTION_TOPICS,
)

logger = logging.getLogger(__name__)


class MQTTService:

    def __init__(self):
        self.client = MQTTClient()
        self._started = False

        self.publisher = MQTTPublisher(self.client)
        self.subscriber = MQTTSubscriber(self.client)

        self.subscriber.set_message_handler(self._handle_message)

        for topic in MQTT_SUBSCRIPTION_TOPICS:
            self.subscriber.subscribe(topic, qos=1)

    def start(self):
        if self._started:
            logger.warning("MQTT service is already running.")
            return

        self.client.connect()
        self._started = True

        logger.info("MQTT service started successfully.")

    def stop(self):
        if not self._started:
            return

        self.client.disconnect()
        self._started = False

        logger.info("MQTT service stopped successfully.")

    # ---------------------------------
    # HANDLE ESP32 MQTT MESSAGES
    # ---------------------------------

    def _handle_message(self, message):
        payload = self.subscriber.decode_message(message)

        if message.topic == MQTT_VALVE_ACK_TOPIC:
            logger.info(
                "VALVE ACK RECEIVED: %s",
                payload,
            )

        elif message.topic == MQTT_VALVE_STATUS_TOPIC:
            logger.info(
                "VALVE STATUS RECEIVED: %s",
                payload,
            )

    @property
    def is_running(self):
        return self._started

    @property
    def is_connected(self):
        return self.client.is_connected
