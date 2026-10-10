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






import logging

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

        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=30,
        )

        self._connected = False
        self._loop_started = False

    def connect(self):
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
        if not self._loop_started:
            return

        try:
            self.client.disconnect()
        finally:
            self.client.loop_stop()
            self._loop_started = False
            self._connected = False

        logger.info("MQTT client stopped.")

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):
        if reason_code == 0:
            self._connected = True
            logger.info("MQTT connected successfully.")
        else:
            self._connected = False
            logger.error(
                "MQTT connection rejected. Reason code: %s",
                reason_code,
            )

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties,
    ):
        self._connected = False

        logger.warning(
            "MQTT disconnected. Reason code: %s",
            reason_code,
        )

    @property
    def is_connected(self):
        return self.client.is_connected()

    @property
    def is_loop_running(self):
        return self._loop_started
