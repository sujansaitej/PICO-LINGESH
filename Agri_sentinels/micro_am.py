import network
import urequests
import time
import json
from machine import Pin, ADC
import dht

# Set up the sensors
dht_pin = Pin(15)  # DHT11/DHT22 sensor pin
soil_moisture_pin = ADC(Pin(26))  # Analog input for soil moisture
mq135_pin = ADC(Pin(27))  # Analog input for MQ135

# DHT sensor instance
dht_sensor = dht.DHT11(dht_pin)  # Use DHT11 or DHT22 depending on your sensor

# Wi-Fi details
ssid = "Your_SSID"
password = "Your_PASSWORD"

# Flask server IP address and endpoint
server_url = "http://<your-flask-server-ip>:5000/sensor_data"


# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
while not wlan.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Connected to Wi-Fi, IP Address:", wlan.ifconfig()[0])

# Function to read sensor values
def read_sensors():
    try:
        # Read temperature and humidity from DHT sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        # Read soil moisture (assuming it's connected to ADC pin)
        soil_moisture_value = soil_moisture_pin.read_u16()  # 16-bit value (0-65535)
        soil_moisture_percentage = soil_moisture_value / 65535 * 100  # Convert to percentage

        # Read air quality from MQ135 sensor (assuming it's connected to ADC pin)
        mq135_value = mq135_pin.read_u16()  # 16-bit value (0-65535)

        # Return sensor data as a dictionary
        return {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture_percentage,
            "mq135_value": mq135_value
        }
    except Exception as e:
        print("Error reading sensors:", e)
        return None

# Post sensor data to the server
def post_data(sensor_data):
    try:
        # Additional parameters
        soil_type = "loamy"
        plant_type = "tomato"

        # Prepare the payload
        payload = {
            "sensor_data": sensor_data,
            "soil_type": soil_type,
            "plant_type": plant_type
        }

        # Send POST request to the Flask server
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(server_url, data=json.dumps(payload), headers=headers)
        print("Response Code:", response.status_code)
        print("Response Text:", response.text)
        response.close()
    except Exception as e:
        print("Failed to post data:", e)

# Main loop to read sensors and post data every 10 seconds
while True:
    sensor_data = read_sensors()
    if sensor_data:
        post_data(sensor_data)
    time.sleep(10)
