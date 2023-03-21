from PIL.ExifTags import TAGS
from PIL import Image
import requests
import psycopg2
import os
import time




def get_weather_data(lat_long, date):
    api_key = "2b4a3252534e0a5ccd7a7baef67120a3" # ! MOVE TO ENV FILE BEFORE DEPLOYMENT || os.environ.get('WEATHER_API_KEY')
    url = f'http://api.weatherstack.com/current?access_key={api_key}&query={lat_long}&historical_date={date}'
    res  = requests.get(url)
    data = res.json()

    return data


