
VALVE_CONTROL = "aquapod/test/{}/valve/set"

DEVICE_STATUS = "aquapod/test/+/status"

MQTT_VALVE_SET_TOPIC = "aquapod/test/Valve_Device001/valve/set"
MQTT_VALVE_ACK_TOPIC = "aquapod/test/Controller001/ack"
MQTT_VALVE_STATUS_TOPIC = "aquapod/test/Controller001/status"

MQTT_PUMP_SET_TOPIC = "aquapod/test/Pump_Device001/pump/set"

MQTT_SUBSCRIPTION_TOPICS = [
    MQTT_VALVE_ACK_TOPIC,
    MQTT_VALVE_STATUS_TOPIC,
    DEVICE_STATUS,
]
