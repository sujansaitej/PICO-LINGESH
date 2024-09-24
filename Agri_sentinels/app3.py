from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import requests

app = Flask(__name__)

# Store sensor data globally to access later
latest_sensor_data = {}

# Configure Gemini API Key (using environment variable for security)
api_key = os.getenv('API_KEY', 'AIzaSyDMk5Rt__dgYy1asyqofi4nAygZUEZC0Y0')
genai.configure(api_key=api_key)

# Telegram Bot API details
telegram_api_url = "https://api.telegram.org/bot<your-bot-token>/sendMessage"
chat_id = "<your-chat-id>"

# Route for receiving sensor data from the Pico board
@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    global latest_sensor_data
    try:
        # Receive and store sensor data
        latest_sensor_data = request.json.get('sensor_data', {})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Error receiving sensor data:", e)
        return jsonify({"error": "Internal Server Error"}), 500

# Route for displaying the web form
@app.route('/')
def index():
    return render_template('index.html')

# Route for getting the latest sensor data dynamically in the frontend
@app.route('/get_latest_sensor_data', methods=['GET'])
def get_latest_sensor_data():
    if not latest_sensor_data:
        return jsonify({"error": "No sensor data available"}), 400
    return jsonify(latest_sensor_data), 200

# Route for handling form submissions from the UI
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        # Get the JSON data from the client-side
        data = request.json

        if not data or 'sensor_data' not in data or 'soil_type' not in data or 'plant_type' not in data:
            return jsonify({"error": "Missing data"}), 400  # Bad Request

        sensor_data = data['sensor_data']
        soil_type = data['soil_type']
        plant_type = data['plant_type']

        # Gemini prompt to dynamically generate plant health report
        prompt = f"Given the sensor data: temperature is {sensor_data['temperature']} degrees, " \
                 f"humidity is {sensor_data['humidity']}%, soil moisture level is {sensor_data['soil_moisture']}, " \
                 f"and MQ135 value is {sensor_data['mq135_value']}, for a {plant_type} planted in {soil_type}, " \
                 f"assess the plant's health and provide care recommendations."

        # Generate a response using the Gemini AI API
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        report = response.text.strip()

        # Send the report to the Telegram bot
        telegram_payload = {
            'chat_id': chat_id,
            'text': report
        }
        telegram_response = requests.post(telegram_api_url, data=telegram_payload)

        if telegram_response.status_code == 200:
            print("Message successfully sent to Telegram.")
        else:
            print(f"Failed to send message to Telegram. Status code: {telegram_response.status_code}")

        # Return the Gemini AI-generated report to the front end
        return jsonify({
            "health_status": "Good",
            "recommendations": report
        }), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
