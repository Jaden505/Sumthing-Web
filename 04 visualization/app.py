from flask import Flask, render_template, request, redirect
from flask import flash # messages op html pagina https://www.youtube.com/watch?v=T1PLBEEZU8o 
from flask_navigation import Navigation
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import datetime as dt
import pandas as pd
import json

import plotly

from helper_visualisation import plot_map, plotbar
from db_READ import select_lat_lon, select_batches, select_all_comparable_image
from db_READ import select_batches_metadata, select_batches_totalscore


import dotenv
import os

dotenv.load_dotenv()
DATABASE_TO_URI = os.environ['DATABASE_TO_URI']

app = Flask(__name__)
nav = Navigation(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


nav.Bar('top', [
    nav.Item('Home', 'index'),
    nav.Item('Stats', 'stats'),
    nav.Item('Visualisatie', 'visualisatie'),
    nav.Item('Upload', 'upload'),
    nav.Item('Compare', 'compare'),
])

@app.route('/')
def index():
    tijd = dt.datetime.now()
    files =[]
    return render_template('index.html', files=files, time=tijd)


@app.route('/visualisatie')
def visualisatie():
    batches = list()
    for i in select_batches(DATABASE_TO_URI):
        batches.append(i[0])

    return render_template('visualisatie.html', files=batches)

@app.route('/stats')
def stats():
    results = select_batches_totalscore(DATABASE_TO_URI)
    df = pd.DataFrame(results,columns =['batch_key', 'batch_name', 'proof_image_name', 'score_duplicate_tree'])
    fig = plotbar(df)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('stats.html', title="Home",graphJSON=graphJSON)


@app.route('/compare')
def compare():

    images = select_all_comparable_image()

    return render_template('compare.html', images = images)


@app.route('/visualisatie/map')
def map():
    import pprint
    graphJSON = None
    metadata = None
    
    batches = list()
    for i in select_batches(DATABASE_TO_URI):
       batches.append(i[0])
    batch_key = list()

    requested_batches = request.args.get('batches')

    if requested_batches:
        for batch in requested_batches.split(','):
            batch_key.append(int(batch.split('_')[0]))

        metadata = select_batches_metadata(DATABASE_TO_URI, batch_key)

        df_images = pd.DataFrame(columns =['picture_name', 'lat', 'lon', 'time', 'batch_key', 'score_duplicate_tree'])    
        lat_lon_results = select_lat_lon(DATABASE_TO_URI, batch_key)
        for lat_lon_data in lat_lon_results:
            df = pd.DataFrame(lat_lon_data, columns =['picture_name', 'lat', 'lon', 'time', 'batch_key', 'score_duplicate_tree'])
            df_images = pd.concat([df_images, df], ignore_index=True)

        fig = plot_map(df_images, 'path') # scatter / path

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    header="- Bomen in Europa"
    description = """
    kaart van bomen
    """
    return render_template('visualisatie.html', metadata=metadata, files=batches, graphJSON=graphJSON, header=header, description=description)


if __name__ == '__main__':
    app.run(debug=True)

