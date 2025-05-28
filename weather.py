import requests

API_KEY = "3eec4ee8c46444449e0181022252605"

districts = {
    "Dehradun": ["Dehradun", "Rishikesh", "Vikasnagar", "Chakrata", "Herbertpur", "Doiwala"],
    "Haridwar": ["Haridwar", "Roorkee", "Laksar", "Bahadrabad"],
    "Nainital": ["Nainital", "Haldwani", "Ramnagar", "Kaladhungi", "Bhimtal"],
    "Udham Singh Nagar": ["Rudrapur", "Kashipur", "Khatima", "Sitarganj", "Jaspur"],
    "Pauri Garhwal": ["Pauri", "Kotdwar", "Srinagar", "Lansdowne", "Satpuli"],
    "Chamoli": ["Gopeshwar", "Joshimath", "Karnaprayag", "Nandaprayag", "Chamoli"],
    "Rudraprayag": ["Rudraprayag", "Agastyamuni", "Ukhimath", "Jakholi"],
    "Tehri Garhwal": ["New Tehri", "Narendranagar", "Chamba", "Ghansali"],
    "Almora": ["Almora", "Ranikhet", "Dwarahat", "Jainti"],
    "Bageshwar": ["Bageshwar", "Kanda", "Kapkot"],
    "Pithoragarh": ["Pithoragarh", "Didihat", "Berinag", "Dharchula", "Munsyari"],
    "Champawat": ["Champawat", "Lohaghat", "Tanakpur", "Purnagiri"]
}

def classify_weather(description):
    description = description.lower()
    if "clear" in description or "sunny" in description:
        return 0
    elif "light rain" in description or "drizzle" in description or "cloudy" in description:
        return 1
    elif "moderate rain" in description or "heavy rain" in description or "thunderstorm" in description:
        return 2
    elif "flood" in description or "cyclone" in description or "storm" in description:
        return 3
    else:
        return -1  # Unknown or unclassified

def get_weather_code(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_description = data['current']['condition']['text']
        print(f"{city}: {weather_description}")
        return classify_weather(weather_description)
    except Exception as e:
        print(f"Error fetching data for {city}: {e}")
        return -1

def get_district_weather(district_name):
    if district_name not in districts:
        print(f"District '{district_name}' not found.")
        return []

    city_list = districts[district_name]
    weather_codes = []

    for city in city_list:
        code = get_weather_code(city)
        weather_codes.append(code)

    return weather_codes
    
if __name__ == "__main__":
    district_input = input("Enter district name: ")
    get_district_weather(district_input)
