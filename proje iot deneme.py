import random
import time
import json
import base64
from paho.mqtt import client as mqtt

# Azure IoT Hub connection details
IOT_HUB_HOST = "cdv-iot-platform-hu-random-name.azure-devices.net"

# List of Trucks (Unique Device IDs and Their Pre-generated SAS Tokens)
TRUCKS = [
    {
        "device_id": "truck-001",
        "sas": "SharedAccessSignature sr=cdv-iot-platform-hu-random-name.azure-devices.net%2Fdevices%2Ftruck-001&sig=1sHoyy%2BlXesFt2TBIFy%2BIf21nqC8zNtgmLTIKRvWxTg%3D&se=1768871784"
    },
    {
        "device_id": "truck-002",
        "sas": "SharedAccessSignature sr=cdv-iot-platform-hu-random-name.azure-devices.net%2Fdevices%2Ftruck-002&sig=u0WErfVJHKT80rIlZW6sV94KkH1Qv%2BvJmccRiZA93Y4%3D&se=1768871789"
    },
    {
        "device_id": "truck-003",
        "sas": "SharedAccessSignature sr=cdv-iot-platform-hu-random-name.azure-devices.net%2Fdevices%2Ftruck-003&sig=cQULgUxpmK1y%2BafLizInndxVFUK6DWF4%2Fy%2FXQHcbB0E%3D&se=1768871795"
    },
    {
        "device_id": "truck-004",
        "sas": "SharedAccessSignature sr=cdv-iot-platform-hu-random-name.azure-devices.net%2Fdevices%2Ftruck-004&sig=e4VLPUhAjIBeRpTs9isdD20VXTLEtbITA6hYZCSEcNw%3D&se=1768871804"
    },
    {
        "device_id": "truck-005",
        "sas": "SharedAccessSignature sr=cdv-iot-platform-hu-random-name.azure-devices.net%2Fdevices%2Ftruck-005&sig=eUZI0VoH26ECzG5OlzyiZf6OPZvaUOs%2FT0gcn05VEZc%3D&se=1768871815"
    }
]

# MQTT client event handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"{userdata['device_id']} connected successfully.")
    else:
        print(f"{userdata['device_id']} connection failed. Code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published for {userdata['device_id']}. Message ID: {mid}")

# Function to simulate sensor data
def simulate_sensor_data(device_id):
    temperature = round(random.uniform(20, 30), 2)
    humidity = round(random.uniform(40, 60), 2)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    return {
        "device_id": device_id,
        "sensor_data": {
            "temperature": temperature,
            "humidity": humidity,
        },
        "timestamp": timestamp
    }

# Function to encode data to Base64
def encode_to_base64(data):
    json_data = json.dumps(data)
    return base64.b64encode(json_data.encode('utf-8')).decode('utf-8')

# Function to decode Base64 to original JSON
def decode_from_base64(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data)
    return json.loads(decoded_bytes.decode('utf-8'))

# Function to create MQTT client for a truck
def create_mqtt_client(truck):
    client = mqtt.Client(client_id=truck["device_id"])
    client.username_pw_set(
        username=f"{IOT_HUB_HOST}/{truck['device_id']}/?api-version=2021-04-12",
        password=truck["sas"]
    )
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.user_data_set(truck)
    client.tls_set()  # IoT Hub security with TLS
    client.connect(IOT_HUB_HOST, port=8883)  # IoT Hub MQTT port
    return client

# Create MQTT clients for all trucks
clients = []
for truck in TRUCKS:
    client = create_mqtt_client(truck)
    client.loop_start()
    clients.append(client)

# Main loop to send simulated data
try:
    while True:
        for truck, client in zip(TRUCKS, clients):
            sensor_data = simulate_sensor_data(truck["device_id"])
            
            # Encode message to Base64
            message_encoded = encode_to_base64(sensor_data)
            
            print(f"Publishing data for {truck['device_id']}: {sensor_data}")
            print(f"Encoded message: {message_encoded}")
            
            client.publish(f"devices/{truck['device_id']}/messages/events/", message_encoded, qos=1)
        time.sleep(10)
except KeyboardInterrupt:
    print("Program stopped.")
finally:
    for client in clients:
        client.loop_stop()
        client.disconnect()
