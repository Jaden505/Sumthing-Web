import datetime as dt
import os

import cv2
import numpy as np
import requests
import tensorflow as tf
from helper_img_metadata import extract_metadata
from db_CRUD import update_image_score, insert_weather

def weather_check(lat, lon, datetime, hour):
    api_key = open(r"api_key").read()
    url = "http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
    response = requests.get(url,
                            params=f"q={lat},{lon}&date={datetime}&key={api_key}&format=json")
    return response.json()["data"]["weather"][0]["hourly"][hour]["weatherDesc"][0]["value"]

def get_weather_data(path):
    
    duplicateMetadata = extract_metadata(path)
    first_file = os.listdir(path)[0]
    weather_check_desc = []
    cwd = os.getcwd()
    path_for_save = os.path.join(cwd,  "Saved_model_weather")
    model = tf.keras.models.load_model(path_for_save)

    for i in range(8):
        img_lat = None# get from db
        img_lon = None# get from db
        img_datetime = None# get from db
        date_hour = int(round((img_datetime.hour / 3), 0))
    
        weather_check_desc.append(str(weather_check(img_lat, img_lon, img_datetime, i)).lower())
        insert_weather(int(first_file.split("_")[0]), img_datetime, weather_check_desc[i], i)

    for filename in os.listdir(path):
        img_datetime = duplicateMetadata.get(filename).get("datetime")
        img_datetime = dt.datetime.strptime(img_datetime, "%Y:%m:%d %H:%M:%S")
        

        # ( Cloudy( 0 ), Sunny( 1 ), Rainy( 2 ), Snowy( 3 ), Foggy( 4 ))
        img = cv2.imread(os.path.join(path, filename))
        img_size = 300
        shape = (img_size, img_size)
        check_image = cv2.resize(img / 255, shape)
        check_image = np.expand_dims(check_image / 255, 0)
        score = model.predict(check_image)
        for i in range(len(weather_check_desc)):
            if i == date_hour:
                if "cloud" in weather_check_desc[i]:
                    score_num = score[0][0]
                elif "sun" in weather_check_desc[i] or "clear" in weather_check_desc[i]:
                    score_num = score[0][1]
                elif "rain" in weather_check_desc[i]:
                    score_num = score(check_image)[0][2]
                elif "snow" in weather_check_desc[i]:
                    score_num = score[0][3]
                elif "fog" in weather_check_desc[i]:
                    score_num = score(check_image)[0][4]

                update_image_score(filename, score_num, 5)

