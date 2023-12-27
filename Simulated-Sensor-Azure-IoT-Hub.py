# SUMMARY ####################################################################################################################
# This Python script simulates 3 different sensors. The sensors can record the temperature and humidity. 
# For this use case, three identical sensors are created in Azure IoT Hub: "Room0", "Room1" and "Room3". The script then 
# connects to the devices created in Azure IoT Hub, which represent the sensors. The simulated data for temperature and 
# humidity is sent to these every 10 seconds.
#############################################################################################################################

# IMPORT NECESSARY LIBRARIES ################################################################################################
import time
from azure.iot.device import IoTHubDeviceClient, Message #If not installed use: pip install azure-iot-device
from random import uniform

# 1. DEFINE CONNECTION STRINGS ##############################################################################################
# You need this connection string to connect to the created devices in Azure IoT Hub. In this Use Case.
# You can find the conncetion string of each device in your Azure IoT Hub - Devices. Click to your device and copy Primary 
# connection string.
connection_string_room0 = "<Your-Room0-Primary-Connection-String>"
connection_string_room1 = "<Your-Room1-Primary-Connection-String>"
connection_string_room2 = "<Your-Room2-Primary-Connection-String>"


# Store all Rooms and their Connection Strings in a List
connection_strings_rooms = {
    "Room0": connection_string_room0,
    "Room1": connection_string_room1,
    "Room2": connection_string_room2,
}


# GENERATE HUMIDITY #######################################################################################################
# A "realistic" humidity will be created in this function. 
def generate_humidity():
    
    # Set start humidity
    start_humidity = 60
    
    # Change humidity between +5% and -5% from the current value
    change_humidity = uniform(-5, 5)
    
    # Round humidity by one decimal place (e.g. 5.12345 --> 5.1)
    new_humidity = round(start_humidity + change_humidity, 1)
    
    # Return humidity, just allowed between 10% and 95%
    return max(10, min(95, new_humidity))



# GENERATE TEMPERATURE #################################################################################################
# A "realistic" temperature will be created in this function. 
def generate_temperature():
    
    # Set start temperature
    start_temperature = 20
    
    # Change temperature between +5% and -5% from the current value
    change_temperature = uniform(-5, 5)
    
    # Round temperature by one decimal place (e.g. 5.12345 --> 5.1)
    new_temperature = round(start_temperature + change_temperature, 1)
    
    # Return humidity, just allowed between -50 degrees and 100 degrees
    return max(-50, min(100, new_temperature))

# SEND SIMULATED DATA TO AZURE IOT HUB ################################################################################
def send_simulated_data(device_client, room, temperature, humidity):
    
    # Define payload
    payload = {"Temperature": temperature, "Humidity": humidity}
    
    # Convert payload into String
    message_to_send = Message(str(payload))
    
    # Send message to Azure IoT Hub
    device_client.send_message(message_to_send)
    print(f"Message sent from {room} --> Temperature: {temperature}; Humidity: {humidity}")

def main():
    
    # Define empty list for the rooms and their connection strings
    devices = {}
    for room, connection_string in connection_strings_rooms.items():
        devices[room] = IoTHubDeviceClient.create_from_connection_string(connection_string)

    try:
        for device_client in devices.values():
            
            # Connect to Azure IoT Hub device
            device_client.connect()

        while True:
            for room, device_client in devices.items():
                
                # 1. Generate Temperature
                temperature = generate_temperature()
                
                # 2. Generate Humidity
                humidity = generate_humidity()
                
                # 3. Send Data to Azure IoT Hub´s devices
                send_simulated_data(device_client, room, temperature, humidity)
                
            # Wait for 10 seconds to send new Data
            time.sleep(10)

    except KeyboardInterrupt:
        print("Script terminated by user.")
    finally:
        for device_client in devices.values():
            
            # Disconnect
            device_client.disconnect()

if __name__ == "__main__":
    main()
