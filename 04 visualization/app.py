from flask import Flask, render_template, url_for, request, redirect, Response, flash
from flask import flash # messages op html pagina https://www.youtube.com/watch?v=T1PLBEEZU8o 
from flask_navigation import Navigation
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import datetime as dt
import pandas as pd
import json

import plotly
import plotly.express as px
import plotly.graph_objects as go

from ETL_images.functions.functions import move_zip, plot_map, plotbar
from ETL_images.functions.functions import select_lat_lon, select_batches, find_comparable_images, delete_image_from_database
from ETL_images.functions.functions import uploads_zip_checker, update_duplicate_tree_score_database
from ETL_images.functions.database import select_batches_metadata, batches_totalscore
from ETL_images.main_images import main

import dotenv
import os

dotenv.load_dotenv()
DATABASE_TO_URI = os.environ['DATABASE_TO_URI']

app = Flask(__name__)
nav = Navigation(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_DIRECTORY'] = 'uploads'
app.config['IMAGE_DIRECTORY'] = 'zipimages'
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024 # 512MB
app.config['ALLOWED_EXTENSIONS'] = ['.zip']

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
    files = os.listdir(app.config['UPLOAD_DIRECTORY'])
    return render_template('index.html', files=files, time=tijd)

@app.route('/test', methods=['GET'])
def test():
    tijd = dt.datetime.now()
    files = os.listdir(app.config['UPLOAD_DIRECTORY'])
    try:
        data = request.args.getlist('mymultiselect')
        if data:
            print(data)
        else:
            print('empty list')
    except Exception as err:
        flash(err)
    
    return render_template('index.html', files=files, time=tijd)


@app.route('/visualisatie')
def visualisatie():
    batches = list()
    for i in select_batches(DATABASE_TO_URI):
        batches.append(i[0])

    return render_template('visualisatie.html', files=batches)

@app.route('/stats')
def stats():
    results = batches_totalscore(DATABASE_TO_URI)
    df = pd.DataFrame(results,columns =['batch_key', 'batch_name', 'proof_image_name', 'score_duplicate_tree'])
    fig = plotbar(df)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('stats.html', title="Home",graphJSON=graphJSON)


@app.route('/upload')
def upload():
    files = os.listdir(app.config['UPLOAD_DIRECTORY'])
    return render_template('upload.html', files=files)

@app.route('/process', methods=['POST', 'GET'])
def proces_file():
    files = os.listdir(app.config['UPLOAD_DIRECTORY'])

    results_zip = uploads_zip_checker() # checks uploads folder for invalid files
    checker = False
    for zip in results_zip:
        invalid_files = results_zip[zip]['Invalid_File']
        if invalid_files != 0:
            checker = True
            flash(f'{zip} contains invalid {invalid_files} files')

    if checker: # if upload folder contains zips with invalid files the code returns early
        return render_template('upload.html', files=files)
    elif checker == False:
        ##TODO pipeline toevoegen (move -> unzip -> checks -> results to database)
        for zip2 in files:
            move_zip(zip2)
        main()
        return render_template('upload.html', files=files)



@app.route('/delete_file/<file>', methods=['POST', 'GET'])
def delete_file(file):
    file_path = os.path.join(os.getcwd(), app.config['UPLOAD_DIRECTORY'], file)
    os.remove(file_path)

    return redirect('/upload')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file:
            extension = os.path.splitext(file.filename)[1].lower()
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'File is not a zip.' 
            file.save(os.path.join(
                app.config['UPLOAD_DIRECTORY'],
                secure_filename(file.filename)
        ))

    except RequestEntityTooLarge:
        return 'File is larger than the 512MB limit.'


    return redirect('/upload')

@app.route('/compare')
def compare():

    images = find_comparable_images()

    return render_template('compare.html', images = images)

@app.route('/compare/button_no/<proof_key>', methods=['POST', 'GET'])
def button_no(proof_key):
    # update score_duplicate_tree to none
    update_duplicate_tree_score_database(None, proof_key)
    return redirect('/compare')

@app.route('/compare/button_yes/<proof_key>', methods=['POST', 'GET'])
def button_yes(proof_key):

    update_duplicate_tree_score_database(100, proof_key)
    return redirect('/compare')


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

