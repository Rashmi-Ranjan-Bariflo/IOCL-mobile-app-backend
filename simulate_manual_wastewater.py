import json
import time
import uuid
import random
import logging
import threading

from datetime import datetime
from zoneinfo import ZoneInfo

import paho.mqtt.client as mqtt
from decouple import config

from simulate_wastewater import BASE_TOPIC
# ---------------------------------------------------------
# MQTT CONFIGURATION
# ---------------------------------------------------------

MQTT_BROKER = config("MQTT_BROKER")
MQTT_PORT = config("MQTT_PORT", default=1883, cast=int)
MQTT_USERNAME = config("MQTT_USER")
MQTT_PASSWORD = config("MQTT_PASSWORD")

MQTT_CLIENT_ID = "WASTEWATER_MANUAL_SIMULATOR_001"

VALVE_CODE = "Valve_Device001"
PUMP_CODE = "Pump_Device001"
FLOW_SENSOR_CODE = "Flow_Sensor_001"
LEVEL_SENSOR_CODE = "Level_Sensor_001"

VALVE_SET_TOPIC = f"{BASE_TOPIC}/{VALVE_CODE}/set"
PUMP_SET_TOPIC = f"{BASE_TOPIC}/{PUMP_CODE}/set"

VALVE_STATUS_TOPIC = f"{BASE_TOPIC}/{VALVE_CODE}/status"
PUMP_STATUS_TOPIC = f"{BASE_TOPIC}/{PUMP_CODE}/status"

FLOW_STATUS_TOPIC = f"{BASE_TOPIC}/{FLOW_SENSOR_CODE}/status"
LEVEL_STATUS_TOPIC = f"{BASE_TOPIC}/{LEVEL_SENSOR_CODE}/status"

# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------------------------------------------------
# DEVICE STATES
# ---------------------------------------------------------

device_states = {
    "valve": "OFF",
    "pump": "OFF",
}

sensor_running = True
state_lock = threading.Lock()

# ---------------------------------------------------------
# TIMESTAMP
# ---------------------------------------------------------


def get_timestamp():
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


# ---------------------------------------------------------
# MQTT CLIENT
# ---------------------------------------------------------

client = mqtt.Client(
    client_id="WASTEWATER_MANUAL_SIMULATOR_001",
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)

client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# ---------------------------------------------------------
# PUBLISH STATUS
# ---------------------------------------------------------

def publish_status(topic, event, state, command_id=None):

    payload = {
        "event_id": str(uuid.uuid4()),
        "timestamp": get_timestamp(),
        "state": state,
        "event": event,
    }

    if command_id:
        payload["command_id"] = command_id

    client.publish(topic, json.dumps(payload), qos=1)

    logging.info("%s | %s", topic, payload)


# ---------------------------------------------------------
# VALVE CONTROL
# ---------------------------------------------------------


def control_valve(command, command_id=None):

    with state_lock:

        if command == "ON":

            device_states["valve"] = "ON"

            logging.info("VALVE TURNED ON")

            publish_status(VALVE_STATUS_TOPIC, "VALVE_OPENED", "ON", command_id)

        elif command == "OFF":

            if device_states["pump"] == "ON":
                logging.warning("Cannot close valve while pump is running.")
                return

            device_states["valve"] = "OFF"

            logging.info("VALVE TURNED OFF")

            publish_status(VALVE_STATUS_TOPIC, "VALVE_CLOSED", "OFF", command_id)


# ---------------------------------------------------------
# PUMP CONTROL
# ---------------------------------------------------------


def control_pump(command, command_id=None):

    with state_lock:

        if command == "ON":

            if device_states["valve"] != "ON":
                logging.warning("Cannot start pump. Valve is closed.")
                return

            device_states["pump"] = "ON"

            logging.info("PUMP TURNED ON")

            publish_status(PUMP_STATUS_TOPIC, "PUMP_STARTED", "ON", command_id)

        elif command == "OFF":

            device_states["pump"] = "OFF"

            logging.info("PUMP TURNED OFF")

            publish_status(PUMP_STATUS_TOPIC, "PUMP_STOPPED", "OFF", command_id)


# ---------------------------------------------------------
# RECEIVE DJANGO COMMANDS
# ---------------------------------------------------------


def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:

        logging.info("Connected to MQTT Broker")

        client.subscribe(VALVE_SET_TOPIC, qos=1)
        client.subscribe(PUMP_SET_TOPIC, qos=1)

        logging.info("Subscribed to manual control topics")

    else:
        logging.error("MQTT connection failed: %s", reason_code)


def on_message(client, userdata, message):

    try:

        payload = json.loads(message.payload.decode("utf-8"))

        command = payload.get("command")
        command_id = payload.get("command_id")

        if payload.get("mode") != "MANUAL":
            logging.warning("Ignoring non-manual command")
            return

        if command not in ["ON", "OFF"]:
            logging.warning("Invalid command: %s", command)
            return

        if message.topic == VALVE_SET_TOPIC:

            control_valve(command, command_id)

        elif message.topic == PUMP_SET_TOPIC:

            control_pump(command, command_id)

    except Exception as error:

        logging.exception("Failed to process MQTT command: %s", error)


client.on_connect = on_connect
client.on_message = on_message

# ---------------------------------------------------------
# FLOW SENSOR SIMULATION
# ---------------------------------------------------------


def simulate_flow_sensor():

    while sensor_running:

        with state_lock:
            pump_state = device_states["pump"]

        if pump_state == "ON":
            flow_rate = round(random.uniform(23, 27), 2)
        else:
            flow_rate = 0.0

        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": get_timestamp(),
            "flow_rate": flow_rate,
            "unit": "L/min",
        }

        client.publish(FLOW_STATUS_TOPIC, json.dumps(payload), qos=0)

        logging.info("FLOW SENSOR: %s L/min", flow_rate)

        time.sleep(5)


# ---------------------------------------------------------
# LEVEL SENSOR SIMULATION
# ---------------------------------------------------------


def simulate_level_sensor():

    level = 0.0

    while sensor_running:

        with state_lock:
            pump_state = device_states["pump"]

        if pump_state == "ON":
            level = min(level + random.uniform(1, 3), 100)

        payload = {
            "event_id": str(uuid.uuid4()),
            "timestamp": get_timestamp(),
            "level": round(level, 2),
            "unit": "%",
        }

        client.publish(LEVEL_STATUS_TOPIC, json.dumps(payload), qos=0)

        logging.info("LEVEL SENSOR: %s%%", round(level, 2))

        if level >= 100:
            logging.warning(
                "Tank reached 100%. Manual mode remains under operator control."
            )

        time.sleep(5)


# ---------------------------------------------------------
# START SIMULATOR
# ---------------------------------------------------------


def main():

    logging.info("Starting Manual Wastewater Simulator")

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    client.loop_start()

    time.sleep(2)

    flow_thread = threading.Thread(target=simulate_flow_sensor, daemon=True)

    level_thread = threading.Thread(target=simulate_level_sensor, daemon=True)

    flow_thread.start()
    level_thread.start()

    logging.info("Manual simulator is running.")
    logging.info("Waiting for Django MQTT commands...")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        global sensor_running
        sensor_running = False

        logging.info("Stopping simulator...")

        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
