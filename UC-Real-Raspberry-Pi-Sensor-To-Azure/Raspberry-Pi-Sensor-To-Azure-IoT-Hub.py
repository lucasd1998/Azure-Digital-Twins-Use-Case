import board
import adafruit_dht 

import time
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message
from random import uniform

# Define Connection String for Azure IoT Hub Device
connection_string_device_azure_iot_hub = "HostName=iot-hub-azure-digital-twins-doerr.azure-devices.net;DeviceId=RaspberryPiHumiture;SharedAccessKey=86kRG6dqd3auHgpYyAIjuxNnp0S3bATYCAIoTDMy4kw="

# Set GPIO-Pin for DHT11-Sensor
dht_pin = board.D17

# Create DHT-Object
dht_sensor = adafruit_dht.DHT11(dht_pin)

def main():
    # Create device client
    device_client = IoTHubDeviceClient.create_from_connection_string(connection_string_device_azure_iot_hub)

    try:

        # Connect to Azure IoT Hub Device
        device_client.connect()

        while True:
                
            # Define Log-Time
            log_time = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

            try:
                # Read Temperature from DHT11 Sensor
                temperature = dht_sensor.temperature

                # Read Humidity from DHT11 Sensor
                humidity = dht_sensor.humidity

                # Define Payload with Temperature and Humidity Data
                payload = {"Temperature": temperature, "Humidity": humidity}
                
                # Define Message to send as String
                message_to_send = Message(str(payload))
                
                # Send Message to Device Client
                device_client.send_message(message_to_send)

                print(f"Success:    Timestamp={log_time} --> Temperature={temperature}ºC, Humidity={humidity}%, Status: Sended successfully to Azure IoT Hub!")
                
                time.sleep(60)

            except Exception as e:

                print(f"Error:  Timestamp={log_time} --> Error when reading the DHT sensor: {e}")

    except KeyboardInterrupt:
        # If User interrupt script, print a message
        print("Script terminated by user.")

    finally:
        # Disconnect from Azure IoT Hub Device
        device_client.disconnect()

if __name__ == "__main__":
    main()
