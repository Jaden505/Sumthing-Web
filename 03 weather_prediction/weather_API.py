import requests
import json
import pprint

api_key = open(r"api_key").read()


def get_weather_data(lat_long, date):
    url = f'http://api.weatherstack.com/current?access_key={api_key}&query={lat_long}&historical_date={date}'
    res = requests.get(url)
    data = res.json()

    return data


# Retrieve current weather data by latitude and longitude
# @query: Search by latitude and longitude, example: 52.374_4.890
# Subscription: All plans
def get_current_weather_data(query):
    url = f'http://api.weatherstack.com/current?access_key={api_key}&query={query}'
    res = requests.get(url)
    data = res.json()

    return data


# Return weather forecast up to 14 days in the future
# @query: Search by city name or country name
# Subscription: Professional plan and higher
def predict_weather(query):
    url = f'http://api.weatherstack.com/forecast?access_key={api_key}&query={query}&forecast_days=1&hourly=1'
    res = requests.get(url)
    data = res.json()

    return data


# Return the location by location search
# @query: Search by city name or country name
# Subscription: Standard plan and higher
def location_lookup(query):
    url = f'http://api.weatherstack.com/autocomplete?access_key={api_key}&query={query}'
    res = requests.get(url)
    data = res.json()

    return data


print(pprint.pprint(get_current_weather_data("52.374_4.890")))
# print(pprint.pprint(location_lookup("Amsterdam")))
