import os
import django
import json
import time
import uuid
import logging
import threading
import random

import paho.mqtt.client as mqtt

from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iocl_backend.settings")

django.setup()

from django.conf import settings

MQTT_BROKER = settings.MQTT_BROKER
MQTT_PORT = settings.MQTT_PORT
MQTT_USERNAME = settings.MQTT_USER
MQTT_PASSWORD = settings.MQTT_PASSWORD

MQTT_CLIENT_ID = "WASTEWATER_SIMULATOR_001"

BASE_TOPIC = "aquapod/test"

VALVE_STATUS_TOPIC = f"{BASE_TOPIC}/Valve_Device001/status"
PUMP_STATUS_TOPIC = f"{BASE_TOPIC}/Pump_Device001/status"
FLOW_STATUS_TOPIC = f"{BASE_TOPIC}/Flow_Sensor_001/status"
LEVEL_STATUS_TOPIC = f"{BASE_TOPIC}/Level_Sensor_001/status"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


connection_event = threading.Event()
connection_success = False
connection_lock = threading.Lock()


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=MQTT_CLIENT_ID,
)

client.username_pw_set(
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD,
)


def on_connect(client, userdata, flags, reason_code, properties):

    global connection_success

    with connection_lock:

        connection_success = reason_code == 0

    if connection_success:

        logger.info(
            "MQTT CONNECTED SUCCESSFULLY | Broker: %s | Port: %s",
            MQTT_BROKER,
            MQTT_PORT,
        )

    else:

        logger.error(
            "MQTT CONNECTION REJECTED | Reason: %s",
            reason_code,
        )

    connection_event.set()


def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties,
):

    global connection_success

    with connection_lock:

        connection_success = False

    logger.warning(
        "MQTT DISCONNECTED | Reason: %s",
        reason_code,
    )


client.on_connect = on_connect
client.on_disconnect = on_disconnect


def connect_mqtt():

    logger.info("Connecting to MQTT broker...")

    connection_event.clear()

    with connection_lock:

        global connection_success
        connection_success = False

    try:

        client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            keepalive=60,
        )

        client.loop_start()

        if not connection_event.wait(timeout=15):

            raise TimeoutError("MQTT connection timed out. No CONNACK received.")

        with connection_lock:

            connected = connection_success

        if not connected or not client.is_connected():

            raise ConnectionError(
                "MQTT broker rejected the connection. "
                "Check credentials and broker permissions."
            )

        logger.info("MQTT simulator is ready.")

    except Exception:

        logger.exception("MQTT connection failed.")

        if client.is_connected():

            client.disconnect()

        client.loop_stop()

        raise


def publish_status(topic, payload):

    if not client.is_connected():

        raise ConnectionError("MQTT client is disconnected. Cannot publish status.")

    message = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        **payload,
    }

    message_json = json.dumps(message)

    try:

        result = client.publish(
            topic,
            message_json,
            qos=1,
        )

        if result.rc != mqtt.MQTT_ERR_SUCCESS:

            raise RuntimeError(f"MQTT publish request failed: {result.rc}")

        result.wait_for_publish(timeout=10)

        if not result.is_published():

            raise TimeoutError(f"MQTT publish confirmation timed out: {topic}")

        logger.info(
            "PUBLISHED | Topic: %s | Payload: %s",
            topic,
            message_json,
        )

        return True

    except Exception:

        logger.exception(
            "Failed to publish MQTT status | Topic: %s",
            topic,
        )

        raise


def valve_status(state, event):

    if state not in ["ON", "OFF"]:

        raise ValueError("Invalid valve state.")

    return publish_status(
        VALVE_STATUS_TOPIC,
        {
            "state": state,
            "event": event,
        },
    )


def pump_status(state, event):

    if state not in ["ON", "OFF"]:

        raise ValueError("Invalid pump state.")

    return publish_status(
        PUMP_STATUS_TOPIC,
        {
            "state": state,
            "event": event,
        },
    )


def flow_reading(flow_rate):

    if flow_rate < 0:

        raise ValueError("Flow rate cannot be negative.")

    return publish_status(
        FLOW_STATUS_TOPIC,
        {
            "flow_rate": flow_rate,
            "unit": "L/min",
        },
    )


def level_reading(level):

    if not 0 <= level <= 100:

        raise ValueError("Water level must be between 0 and 100.")

    return publish_status(
        LEVEL_STATUS_TOPIC,
        {
            "level": level,
            "unit": "percent",
        },
    )


def simulate_wastewater():

    logger.info("Starting wastewater simulation.")

    logger.info("Flow sensor monitoring started.")
    logger.info("Level sensor monitoring started.")

    time.sleep(2)

    logger.info("Valve opening...")

    time.sleep(3)

    valve_status(
        "ON",
        "VALVE_OPENED",
    )

    logger.info("Valve opened successfully.")

    time.sleep(2)

    logger.info("Pump starting...")

    pump_status(
        "ON",
        "PUMP_STARTED",
    )

    logger.info("Pump started successfully.")

    time.sleep(2)

    logger.info("Tank filling started.")

    for level in range(10, 101, 10):

        if level == 50:

            flow_rate = 0.0

            logger.warning("Simulating zero flow condition.")

        else:

            flow_rate = round(
                random.uniform(23.0, 27.0),
                2,
            )

        flow_reading(flow_rate)

        level_reading(level)

        logger.info(
            "Tank Level: %s%% | Flow Rate: %s L/min",
            level,
            flow_rate,
        )

        if level >= 100:

            logger.info("Target water level reached.")

            break

        time.sleep(3)

    logger.info("Stopping pump.")

    pump_status(
        "OFF",
        "PUMP_STOPPED",
    )

    time.sleep(2)

    logger.info("Closing valve.")

    valve_status(
        "OFF",
        "VALVE_CLOSED",
    )

    logger.info("Wastewater simulation completed successfully.")


if __name__ == "__main__":

    try:

        connect_mqtt()

        simulate_wastewater()

    except KeyboardInterrupt:

        logger.warning("Simulation stopped by user.")

    except Exception:

        logger.exception("Wastewater simulation failed.")

    finally:

        if client.is_connected():

            client.disconnect()

        client.loop_stop()

        logger.info("MQTT simulator disconnected.")
