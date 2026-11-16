import logging
import threading

import paho.mqtt.client as mqtt
from django.conf import settings

logger = logging.getLogger(__name__)


class MQTTClient:

    def __init__(self):
        self.client = mqtt.Client(
            client_id=settings.MQTT_CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )

        self.client.username_pw_set(
            username=settings.MQTT_USER,
            password=settings.MQTT_PASSWORD,
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe

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
                print("MQTT LOOP ALREADY RUNNING", flush=True)
                return

            print(
                f"MQTT CONNECTING: {settings.MQTT_BROKER}:" f"{settings.MQTT_PORT}",
                flush=True,
            )

            try:
                self.client.connect(
                    host=settings.MQTT_BROKER,
                    port=settings.MQTT_PORT,
                    keepalive=60,
                )

                print(
                    "MQTT BROKER CONNECTION ESTABLISHED. " "Starting network loop...",
                    flush=True,
                )

                self.client.loop_start()
                self._loop_started = True

                print("MQTT NETWORK LOOP STARTED", flush=True)

            except Exception as exc:
                print(
                    f"MQTT CONNECTION ERROR: {exc!r}",
                    flush=True,
                )
                logger.exception("MQTT connection failed.")
                raise

    def disconnect(self):
        with self._lock:
            if not self._loop_started:
                return

            try:
                print("MQTT DISCONNECTING...", flush=True)
                self.client.disconnect()
            finally:
                self.client.loop_stop()
                self._loop_started = False

        print("MQTT CLIENT STOPPED", flush=True)

    def publish(self, topic, payload, qos=1, retain=False):
        if not isinstance(payload, (str, bytes, bytearray)):
            raise TypeError("MQTT payload must be str, bytes, or bytearray.")

        if not self.client.is_connected():
            raise ConnectionError("MQTT broker is not connected.")

        result = self.client.publish(
            topic=topic,
            payload=payload,
            qos=qos,
            retain=retain,
        )

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed. Return code: {result.rc}")

        print(
            f"MQTT PUBLISH QUEUED | Topic: {topic} | Payload: {payload}",
            flush=True,
        )

        return result

    def subscribe(self, topic, qos=1):
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("A valid MQTT topic is required.")

        if qos not in (0, 1, 2):
            raise ValueError("MQTT QoS must be 0, 1, or 2.")

        with self._lock:
            self._subscriptions[topic] = qos

            if not self.client.is_connected():
                print(
                    f"MQTT SUBSCRIPTION SAVED: {topic}",
                    flush=True,
                )
                return None

            result, mid = self.client.subscribe(topic, qos)

        if result != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                f"MQTT subscription failed for {topic}. " f"Return code: {result}"
            )

        print(
            f"MQTT SUBSCRIBE REQUESTED | Topic: {topic} | MID: {mid}",
            flush=True,
        )

        return mid

    def set_message_callback(self, callback):
        if not callable(callback):
            raise TypeError("Message callback must be callable.")

        self._message_callback = callback
        print("MQTT MESSAGE CALLBACK REGISTERED", flush=True)

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):
        print(
            f"MQTT ON_CONNECT CALLBACK | Reason: {reason_code}",
            flush=True,
        )

        if reason_code != 0:
            print(
                f"MQTT CONNECTION REJECTED: {reason_code}",
                flush=True,
            )
            return

        print("MQTT CONNECTED SUCCESSFULLY", flush=True)

        with self._lock:
            subscriptions = list(self._subscriptions.items())

        if not subscriptions:
            print("NO MQTT SUBSCRIPTIONS REGISTERED", flush=True)
            return

        for topic, qos in subscriptions:
            result, mid = client.subscribe(topic, qos)

            if result != mqtt.MQTT_ERR_SUCCESS:
                print(
                    f"MQTT SUBSCRIBE FAILED: {topic}",
                    flush=True,
                )
            else:
                print(
                    f"MQTT SUBSCRIBE REQUESTED | " f"Topic: {topic} | MID: {mid}",
                    flush=True,
                )

    def _on_subscribe(
        self,
        client,
        userdata,
        mid,
        reason_code_list,
        properties,
    ):
        print(
            f"MQTT SUBSCRIPTION ACKNOWLEDGED | "
            f"MID: {mid} | Reasons: {reason_code_list}",
            flush=True,
        )

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties,
    ):
        print(
            f"MQTT DISCONNECTED | Reason: {reason_code} | "
            f"Flags: {disconnect_flags}",
            flush=True,
        )

    def _on_message(self, client, userdata, message):
        payload = message.payload.decode(
            "utf-8",
            errors="replace",
        )

        print(
            f"MQTT MESSAGE RECEIVED | " f"Topic: {message.topic} | Payload: {payload}",
            flush=True,
        )

        callback = self._message_callback

        if callback is None:
            print("MQTT MESSAGE HANDLER NOT REGISTERED", flush=True)
            return

        try:
            callback(message)
        except Exception:
            logger.exception("MQTT message handler failed.")

    @property
    def is_connected(self):
        return self.client.is_connected()

    @property
    def is_loop_running(self):
        return self._loop_started
