# # mqtt/client.py

# import logging

# import paho.mqtt.client as mqtt
# from django.conf import settings


# logger = logging.getLogger(__name__)


# class MQTTClient:
#     def __init__(self):
#         self.client = mqtt.Client(
#             callback_api_version=mqtt.CallbackAPIVersion.VERSION2
#         )

#         self.client.username_pw_set(
#             username=settings.MQTT_USER,
#             password=settings.MQTT_PASSWORD,
#         )

#         self.client.on_connect = self._on_connect
#         self.client.on_disconnect = self._on_disconnect

#         self._connected = False

#     def connect(self):
#         self.client.connect_async(
#             host=settings.MQTT_BROKER,
#             port=settings.MQTT_PORT,
#             keepalive=60,
#         )

#         self.client.loop_start()

#     def disconnect(self):
#         self.client.loop_stop()
#         self.client.disconnect()

#     def _on_connect(self, client, userdata, flags, reason_code, properties):
#         if reason_code == 0:
#             self._connected = True
#             logger.info("MQTT connected successfully.")
#         else:
#             self._connected = False
#             logger.error(
#                 "MQTT connection failed. Reason code: %s",
#                 reason_code,
#             )

#     def _on_disconnect(
#         self,
#         client,
#         userdata,
#         disconnect_flags,
#         reason_code,
#         properties,
#     ):
#         self._connected = False

#         logger.warning(
#             "MQTT disconnected. Reason code: %s",
#             reason_code,
#         )

#     @property
#     def is_connected(self):
#         return self._connected






# import logging

# import paho.mqtt.client as mqtt
# from django.conf import settings


# logger = logging.getLogger(__name__)


# class MQTTClient:
#     def __init__(self):
#         self.client = mqtt.Client(
#             callback_api_version=mqtt.CallbackAPIVersion.VERSION2
#         )

#         self.client.username_pw_set(
#             username=settings.MQTT_USER,
#             password=settings.MQTT_PASSWORD,
#         )

#         self.client.on_connect = self._on_connect
#         self.client.on_disconnect = self._on_disconnect

#         self.client.reconnect_delay_set(
#             min_delay=1,
#             max_delay=30,
#         )

#         self._connected = False
#         self._loop_started = False

#     def connect(self):
#         if self._loop_started:
#             logger.warning("MQTT network loop is already running.")
#             return

#         self.client.connect_async(
#             host=settings.MQTT_BROKER,
#             port=settings.MQTT_PORT,
#             keepalive=60,
#         )

#         self.client.loop_start()
#         self._loop_started = True

#         logger.info("MQTT network loop started.")

#     def disconnect(self):
#         if not self._loop_started:
#             return

#         try:
#             self.client.disconnect()
#         finally:
#             self.client.loop_stop()
#             self._loop_started = False
#             self._connected = False

#         logger.info("MQTT client stopped.")

#     def _on_connect(
#         self,
#         client,
#         userdata,
#         flags,
#         reason_code,
#         properties,
#     ):
#         if reason_code == 0:
#             self._connected = True
#             logger.info("MQTT connected successfully.")
#         else:
#             self._connected = False
#             logger.error(
#                 "MQTT connection rejected. Reason code: %s",
#                 reason_code,
#             )

#     def _on_disconnect(
#         self,
#         client,
#         userdata,
#         disconnect_flags,
#         reason_code,
#         properties,
#     ):
#         self._connected = False

#         logger.warning(
#             "MQTT disconnected. Reason code: %s",
#             reason_code,
#         )

#     @property
#     def is_connected(self):
#         return self.client.is_connected()

#     @property
#     def is_loop_running(self):
#         return self._loop_started







import logging
import threading

import paho.mqtt.client as mqtt
from django.conf import settings


logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.username_pw_set(
            username=settings.MQTT_USER,
            password=settings.MQTT_PASSWORD,
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=30,
        )

        self._loop_started = False
        self._subscriptions = {}
        self._message_callback = None
        self._lock = threading.RLock()

    def connect(self):
        with self._lock:
            if self._loop_started:
                logger.warning("MQTT network loop is already running.")
                return

            self.client.connect_async(
                host=settings.MQTT_BROKER,
                port=settings.MQTT_PORT,
                keepalive=60,
            )

            self.client.loop_start()
            self._loop_started = True

        logger.info("MQTT network loop started.")

    def disconnect(self):
        with self._lock:
            if not self._loop_started:
                return

            try:
                self.client.disconnect()
            finally:
                self.client.loop_stop()
                self._loop_started = False

        logger.info("MQTT client stopped.")

    def publish(self, topic, payload, qos=1, retain=False):
        if not isinstance(payload, (str, bytes, bytearray)):
            raise TypeError(
                "MQTT payload must be str, bytes, or bytearray."
            )

        if not self.client.is_connected():
            raise ConnectionError("MQTT broker is not connected.")

        result = self.client.publish(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain,
        )

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                f"MQTT publish failed. Return code: {result.rc}"
            )

        logger.info("MQTT message queued for topic: %s", topic)

        return result

    def subscribe(self, topic, qos=1):
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("A valid MQTT topic is required.")

        if qos not in (0, 1, 2):
            raise ValueError("MQTT QoS must be 0, 1, or 2.")

        with self._lock:
            self._subscriptions[topic] = qos

            if not self.client.is_connected():
                logger.info(
                    "Subscription saved. It will be applied after connection: %s",
                    topic,
                )
                return None

            result, mid = self.client.subscribe(topic, qos)

        if result != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                f"MQTT subscription failed for {topic}. "
                f"Return code: {result}"
            )

        logger.info("MQTT subscription requested: %s", topic)

        return mid

    def set_message_callback(self, callback):
        if not callable(callback):
            raise TypeError("Message callback must be callable.")

        self._message_callback = callback

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):
        if reason_code != 0:
            logger.error(
                "MQTT connection rejected. Reason code: %s",
                reason_code,
            )
            return

        logger.info("MQTT connected successfully.")

        # Restore subscriptions whenever the client reconnects.
        with self._lock:
            subscriptions = list(self._subscriptions.items())

        for topic, qos in subscriptions:
            result, mid = client.subscribe(topic, qos)

            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.error(
                    "Failed to restore subscription for topic: %s",
                    topic,
                )

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties,
    ):
        logger.warning(
            "MQTT disconnected. Reason code: %s",
            reason_code,
        )

    def _on_message(self, client, userdata, message):
        logger.info(
            "MQTT message received on topic: %s",
            message.topic,
        )

        callback = self._message_callback

        if callback is None:
            logger.warning(
                "No message handler registered for topic: %s",
                message.topic,
            )
            return

        try:
            callback(message)
        except Exception:
            logger.exception(
                "Error while handling MQTT message from topic: %s",
                message.topic,
            )

    @property
    def is_connected(self):
        return self.client.is_connected()

    @property
    def is_loop_running(self):
        return self._loop_started
