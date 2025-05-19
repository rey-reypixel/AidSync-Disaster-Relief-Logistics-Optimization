from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
import time
import json
import os
import requests

app = Flask(__name__)
geolocator = Nominatim(user_agent="disaster-relief-uttarakhand")

def get_coordinates(city, district=None):
    if district:
        query = f"{city}, {district}, Uttarakhand, India"
    else:
        query = f"{city}, Uttarakhand, India"
    location = geolocator.geocode(query)
    time.sleep(1)  # respect usage policy
    if location:
        return {"latitude": location.latitude, "longitude": location.longitude}
    else:
        return None

def get_population_density(city, district=None):
    """
    Placeholder: This function should be replaced with a real API call
    or dataset lookup for population density.

    For demonstration, we return a dummy value or fetch from some API.
    """

    # Example of dummy static values for demo purposes
    dummy_density = {
        "Kedarnath": 223,
        "Dharchula":2011,
        "Munsiyari":16.7,
        "Didihat":1631,
        "Bhatwari":1417,
        "Harsil":1403,
        "Nainital":3527,
        "Bhimtal":1955,
        "Mukteshwar":119,
        "Joshimath": 1454,
        "Rini":528,
        "Tapovan":122,
        "Mussoorie":26875,
        "Devprayag":198,
        "Ghansali":93,
        "Uttarkashi":47,
        "Haridwar":1100,
        "Roorkee": 20862,
        "Laksar":1853,
        "Almora":198,
        "Bageshwar":119,
        "Champawat":170,
        "Rudrapur": 3245,
        "Haldwani":958,
    }

    # Try district or city first, fallback to 0
    return dummy_density.get(city, dummy_density.get(district, 0))
@app.route('/', methods=['GET'])
def home():
    return "Disaster Relief API is running. Use POST /get_info to query."

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.json
    city = data.get('city')
    district = data.get('district')

    if not city:
        return jsonify({"error": "City is required"}), 400

    coords = get_coordinates(city, district)
    if not coords:
        return jsonify({"error": "Could not find coordinates"}), 404

    population_density = get_population_density(city, district)

    result = {
        "city": city,
        "district": district,
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "population_density": population_density
    }

    # Save to JSON file (append mode)
    json_file = "disaster_data.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(result)

    with open(json_file, "w") as f:
        json.dump(existing_data, f, indent=4)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
