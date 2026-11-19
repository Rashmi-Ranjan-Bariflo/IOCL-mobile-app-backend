
VALVE_CONTROL = "aquapod/test/{}/valve/set"

DEVICE_STATUS = "aquapod/test/+/status"

# Dynamic controller subscriptions
WAST_WATER_ACK = "aquapod/test/+/ack"
WAST_WATER_STATUS = "aquapod/test/+/status"
WAST_WATER_ALERT = "aquapod/test/+/alert"
WAST_WATER_POWER = "aquapod/test/Controller001/power"
WAST_WATER_HEARTBEAT = "aquapod/test/+/heartbeat"

MQTT_VALVE_SET_TOPIC = "aquapod/test/Valve_Device001/valve/set"
MQTT_VALVE_ACK_TOPIC = "aquapod/test/Controller001/ack"
MQTT_VALVE_STATUS_TOPIC = "aquapod/test/Controller001/status"

MQTT_PUMP_SET_TOPIC = "aquapod/test/Pump_Device001/pump/set"

MQTT_SUBSCRIPTION_TOPICS = [
    # WAST_WATER_ACK,
    # WAST_WATER_STATUS,
    WAST_WATER_ALERT,
    WAST_WATER_POWER,
    # WAST_WATER_HEARTBEAT,
]
