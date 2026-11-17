
import logging
import json

from .client import MQTTClient
from .publisher import MQTTPublisher
from .subscriber import MQTTSubscriber

from .topics import (
    MQTT_VALVE_ACK_TOPIC,
    MQTT_VALVE_STATUS_TOPIC,
    MQTT_SUBSCRIPTION_TOPICS,
    DEVICE_STATUS,
)


logger = logging.getLogger(__name__)


class MQTTService:

    def __init__(self):
        self.client = MQTTClient()
        self._started = False

        self.publisher = MQTTPublisher(self.client)
        self.subscriber = MQTTSubscriber(self.client)

        self.subscriber.set_message_handler(
            self._handle_message
        )

    def start(self):

        if self._started:
            logger.warning("MQTT service is already running.")
            return

        # Connect to MQTT broker
        self.client.connect()

        # Subscribe to configured topics
        subscribed_topics = set(MQTT_SUBSCRIPTION_TOPICS)

        subscribed_topics.add(DEVICE_STATUS)

        for topic in subscribed_topics:
            self.subscriber.subscribe(
                topic,
                qos=1,
            )

        self._started = True

        logger.info("MQTT service started successfully.")

    def stop(self):

        if not self._started:
            return

        self.client.disconnect()
        self._started = False

        logger.info("MQTT service stopped successfully.")

    # ---------------------------------
    # HANDLE ALL ESP32 MQTT MESSAGES
    # ---------------------------------

    def _handle_message(self, message):

        payload = self.subscriber.decode_message(message)

        topic = message.topic

        logger.info(
            "MQTT MESSAGE RECEIVED | Topic: %s | Payload: %s",
            topic,
            payload,
        )

        # ---------------------------------
        # VALVE ACK
        # ---------------------------------

        if topic == MQTT_VALVE_ACK_TOPIC:

            logger.info(
                "VALVE ACK RECEIVED: %s",
                payload,
            )

            return

        # ---------------------------------
        # CONTROLLER STATUS
        # ---------------------------------

        if topic == MQTT_VALVE_STATUS_TOPIC:

            logger.info(
                "CONTROLLER STATUS RECEIVED: %s",
                payload,
            )

            return

        # ---------------------------------
        # INDIVIDUAL DEVICE STATUS
        # ---------------------------------

        if topic.startswith("aquapod/test/") and topic.endswith("/status"):

            parts = topic.split("/")

            if len(parts) != 4:
                logger.warning(
                    "Invalid device status topic: %s",
                    topic,
                )
                return

            device_code = parts[2]

            logger.info(
                "DEVICE STATUS RECEIVED | Device: %s | Payload: %s",
                device_code,
                payload,
            )

            self.handle_device_status(
                device_code=device_code,
                payload=payload,
            )

    # ---------------------------------
    # DEVICE STATUS PROCESSING
    # ---------------------------------

    def handle_device_status(self, device_code, payload):

        try:

            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")

            if isinstance(payload, str):
                payload = json.loads(payload)

            if not isinstance(payload, dict):
                logger.warning(
                    "Invalid device status payload: %s",
                    payload,
                )
                return

            state = payload.get("state")

            logger.info(
                "DEVICE: %s | STATE: %s",
                device_code,
                state,
            )
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.exception(
                "Unable to decode device status for %s",
                device_code,
            )

        except Exception:
            logger.exception(
                "Device status processing failed for %s",
                device_code,
            )

    @property
    def is_running(self):
        return self._started

    @property
    def is_connected(self):
        return self.client.is_connected
