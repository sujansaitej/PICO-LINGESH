import requests
import random
import time
import json

# Flask server URL for receiving sensor data
server_url = "http://<your-flask-server-ip>:5000/sensor_data"

# Function to simulate sensor readings
def simulate_sensor_data():
    # Simulated sensor data
    temperature = random.uniform(15, 35)  # Simulate temperature between 15°C and 35°C
    humidity = random.uniform(30, 90)     # Simulate humidity between 30% and 90%
    soil_moisture_value = random.uniform(0, 65535)  # Simulate raw ADC value for soil moisture
    soil_moisture_percentage = (soil_moisture_value / 65535) * 100  # Convert to percentage
    mq135_value = random.uniform(0, 65535)  # Simulate air quality sensor MQ135 value

    # Simulated sensor data as a dictionary
    sensor_data = {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "soil_moisture": round(soil_moisture_percentage, 2),
        "mq135_value": round(mq135_value, 2)
    }
    return sensor_data

# Function to send data to the Flask server
def post_sensor_data(sensor_data):
    try:
        # Prepare the payload
        payload = {
            "sensor_data": sensor_data,
            "soil_type": "loamy",   # Static value for testing
            "plant_type": "tomato"  # Static value for testing
        }

        # Send POST request to Flask server
        headers = {'Content-Type': 'application/json'}
        response = requests.post(server_url, data=json.dumps(payload), headers=headers)

        # Print response from server
        print(f"Response Code: {response.status_code}")
        print(f"Response Text: {response.text}")
    except Exception as e:
        print(f"Failed to post data: {e}")

# Main loop to simulate data posting every 10 seconds
if __name__ == "__main__":
    while True:
        # Simulate sensor data
        sensor_data = simulate_sensor_data()
        print(f"Simulated Sensor Data: {sensor_data}")

        # Send data to the Flask server
        post_sensor_data(sensor_data)

        # Wait for 10 seconds before sending next batch of data
        time.sleep(10)
