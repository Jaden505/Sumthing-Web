import requests
import json

with open('../config.json') as f:
    config = json.load(f)


def get_weather_data(lat_long, date):
    url = f'http://api.weatherstack.com/current?access_key={config["weather-api-key"]}&query={lat_long}&historical_date={date}'
    res = requests.get(url)
    data = res.json()

    return data


# Retrieve current weather data by latitude and longitude
def get_current_weather_data(lat_long):
    url = f'http://api.weatherstack.com/current?access_key={config["weather-api-key"]}&query={lat_long}'
    res = requests.get(url)
    data = res.json()

    return data


# use . and a space to separate objects, and a space, a = and a space to separate keys from their values:
print(json.dumps(get_current_weather_data("52.374_4.890"), indent=4, separators=(". ", " = ")))
