import random
import time
from datetime import datetime

# ==========================================================
# FAKE DEVICE CONFIGURATION
# ==========================================================

DEVICE_ID = "FAKE-DEVICE-001"
PLANT_ID = 1
EQUIPMENT_ID = 1
SENSOR_ID = 1

# ==========================================================
# GENERATE FAKE SENSOR DATA
# ==========================================================


def generate_sensor_data():

    data = {
        "device_id": DEVICE_ID,
        "plant_id": PLANT_ID,
        "equipment_id": EQUIPMENT_ID,
        "sensor_id": SENSOR_ID,
        "timestamp": datetime.now().isoformat(),
        "ph": round(random.uniform(6.5, 9.5), 2),
        "temperature": round(random.uniform(25.0, 35.0), 2),
        "flow_rate": round(random.uniform(80.0, 150.0), 2),
        "pressure": round(random.uniform(1.5, 5.0), 2),
        "dissolved_oxygen": round(random.uniform(3.0, 8.0), 2),
        "turbidity": round(random.uniform(1.0, 10.0), 2),
    }

    return data


# ==========================================================
# DISPLAY DATA
# ==========================================================


def display_data(data):

    print("\n" + "=" * 60)
    print("             FAKE DEVICE DATA")
    print("=" * 60)
    print(f"Device ID       : {data['device_id']}")
    print(f"Plant ID        : {data['plant_id']}")
    print(f"Equipment ID    : {data['equipment_id']}")
    print(f"Sensor ID       : {data['sensor_id']}")
    print(f"Timestamp       : {data['timestamp']}")
    print("-" * 60)
    print(f"pH              : {data['ph']}")
    print(f"Temperature     : {data['temperature']} °C")
    print(f"Flow Rate       : {data['flow_rate']} m³/h")
    print(f"Pressure        : {data['pressure']} bar")
    print(f"Dissolved O₂    : {data['dissolved_oxygen']} mg/L")
    print(f"Turbidity       : {data['turbidity']} NTU")
    print("=" * 60)


# ==========================================================
# MAIN SIMULATOR
# ==========================================================


def main():

    print("Starting Fake Device Simulator...")
    print(f"Device: {DEVICE_ID}")
    print("Press CTRL+C to stop.\n")

    try:

        while True:

            data = generate_sensor_data()

            display_data(data)

            time.sleep(5)

    except KeyboardInterrupt:

        print("\nFake Device Simulator stopped.")


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    main()
