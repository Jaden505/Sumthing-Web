import os
from PIL import Image

from helper_metadata import *
import datetime as dt


# Extract metadata from image
def get_image_metadata(filepath):
    filename = os.path.basename(filepath)
    dict = {}

    # filename
    dict['proof_image_name'] = filename

    img = Image.open(filepath)
    exif_data = get_exif_data(img)

    if exif_data == {} or 'GPSInfo' not in exif_data or 'DateTime' not in exif_data:
        return None

    # img datetime
    exif_datetime = get_datetime(exif_data)
    datetime = dt.datetime.strptime(exif_datetime, '%Y:%m:%d %H:%M:%S')
    dict['taken_date'] = datetime
    dict['creation_date'] = dt.datetime.now()

    # lat, lon
    lat, lon, alt = get_lat_lon_alt(exif_data)
    dict['latitude'] = lat
    dict['longitude'] = lon
    dict['altitude'] = alt

    #format
    dict['format'] = img.format


    #img data
    dict['device_model'] = get_model(exif_data)
    dict['iso'] = get_iso(exif_data)
    dict['f_number'] = get_f_number(exif_data)
    dict['focal_length'] = get_focal_length(exif_data)
    dict['flash'] = get_flash(exif_data)
    dict['shutterspeed'] = get_shutterspeed(exif_data)
    dict['exposure_time'] = get_exposure_time(exif_data)

    #pixels, dimensions
    dimensions, total_pixels = get_pixels_dimensions(exif_data)
    dict['dimensions'] = dimensions
    dict['total_pixels'] = total_pixels

    return dict
