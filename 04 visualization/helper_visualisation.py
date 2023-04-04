import time
import os, shutil
from PIL import Image

import datetime as dt
import pandas as pd
import json


import plotly
import plotly.express as px
import plotly.graph_objects as go

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from db_READ import AllImage, Batch,connect_database
from db_READ import select_all_comparable_image



def plot_map(df_images, mode):
    if mode == 'scatter':
        fig = px.scatter_mapbox(
            df_images,
            lat="lat",
            lon="lon",
            text="picture_name",
            color='score_duplicate_tree',
            color_continuous_scale=[[0, "green"], [0.75, "yellow"], [1, "red"]],
            range_color=[0, 1],
            hover_data={
                'picture_name': True,
                'time': True},
            zoom=1)
    elif mode == 'path':
        mid_lat = sum(df_images.lat) / len(df_images.lat)
        mid_lon = sum(df_images.lon) / len(df_images.lon)

        marked_img = df_images[['picture_name', 'lat', 'lon', 'time', 'score_duplicate_tree']].dropna()

        fig = px.line_mapbox(
            df_images,
            lat="lat",
            lon="lon",
            text="picture_name",
            color='batch_key',
            hover_data={
                'picture_name': True,
                'time': True},
            zoom=1)

        # fig.add_trace(go.Scattermapbox(
        #     name='marked tree',
        #     mode = "markers",
        #     lon = marked_img.lon,
        #     lat = marked_img.lat,
        #     marker = {'size': 5}))

        fig.add_scattermapbox(
            name='marked tree',
            mode="markers",
            hoverinfo='skip',
            lat=marked_img.lat,
            lon=marked_img.lon)

    # fig.update_traces(hovertemplate="picture_name: %{text.picture_name} <br>geolocation: %{lat}/%{lon} <br>Time: %{text.time}")

    fig.update_layout(
        title="sus score",
        mapbox_style="open-street-map",
        mapbox_zoom=17.5,
        showlegend=True,
        autosize=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            x=0,
            y=1,
            title_font_family="Times New Roman",
            font=dict(
                family="Courier",
                size=12,
                color="black"
            ),
            # bgcolor="white",
            # bordercolor="Black",
            # borderwidth=1
        )
    )
    return fig


def select_lat_lon(url, batch_request):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()
        results = list()
        for key in batch_request:
            stmt = select(
                AllImage.proof_image_name,
                AllImage.latitude,
                AllImage.longitude,
                AllImage.proof_date,
                AllImage.batch_key,
                AllImage.score_duplicate_tree
            ).where(AllImage.batch_key == key).order_by(AllImage.proof_date)
            results.append(session.execute(stmt))
        return results


def select_batches(url):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        stmt = select(
            Batch.batch_name
        ).order_by(Batch.batch_name)

        result = session.execute(stmt)
        return result


def select_batches_metadata(url, batch_request):
    engine, conn = connect_database(url)
    if conn:
        Session = sessionmaker(bind=engine)
        session = Session()

        stmt = select(
            Batch.batch_key,
            Batch.batch_name,
            Batch.center_lat,
            Batch.center_long,
            Batch.first_photo_upload,
            Batch.first_photo_upload,
            AllImage.proof_image_name,
            AllImage.proof_medium
        ).join(Batch, Batch.batch_key == AllImage.batch_key)

        result = session.execute(stmt)
        return result


def find_comparable_images():
    dict_list = []

    for image in select_all_comparable_image():
        image_dict = (image.__dict__)

        dict_list.append(image_dict)

    compare_dict_list = []

    for i in enumerate(dict_list):
        i = i[0]
        if i < len(dict_list) - 1:
            if (dict_list[i]['score_duplicate_tree'] == dict_list[i + 1]['score_duplicate_tree']):
                compare_dict_list.append({"key1": dict_list[i]['proof_key'],
                                          "key2": dict_list[i + 1]['proof_key'],
                                          "proof_large1": dict_list[i]['proof_large'],
                                          "proof_large2": dict_list[i + 1]['proof_large']})

    return compare_dict_list






def plotbar(long_df):
    # fig = px.bar(long_df, x="batch_name", y="score_duplicate_tree", color="batch_name", title="Valid/invalid photo's
    # per batch")
    fig = go.Figure(data=[
        go.Bar(name='Valid', x=long_df.batch_name, y=[long_df.score_duplicate_tree.isna().sum()]),
        go.Bar(name='Invalid', x=long_df.batch_name, y=[long_df.score_duplicate_tree.notna().sum()])])
    # Change the bar mode
    fig.update_layout(barmode='stack')

    return fig
