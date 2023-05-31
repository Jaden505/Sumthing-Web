import os
from PIL import Image

from helper_img_metadata import *
from helper_img_to_aws import upload_image_to_aws
from db_ORM import AllImage
import datetime as dt


# Extract metadata from image
def get_image_metadata(filepath):
    filename = os.path.basename(filepath)

    dict = {}
    # filename
    dict['proof_image_name'] = filename

    # batch key
    batch_id=filename.split('_',1)[0]
    dict['batch_key']=batch_id

    img = Image.open(filepath)
    exif_data = get_exif_data(img)

    if exif_data == {} or 'GPSInfo' not in exif_data or 'DateTime' not in exif_data:
        return None

    # img datetime
    exif_datetime = get_datetime(exif_data)
    datetime = dt.datetime.strptime(exif_datetime, '%Y:%m:%d %H:%M:%S')
    dict['proof_date'] = datetime

    # lat, lon
    lat, lon, alt = get_lat_lon_alt(exif_data)
    dict['latitude'] = lat
    dict['longitude'] = lon
    dict['altitude'] = alt

    #format
    dict['img_format'] = img.format

    #img data
    dict['img_device_model'] = get_model(exif_data)
    dict['img_iso'] = get_iso(exif_data)
    dict['img_f_number'] = get_f_number(exif_data)
    dict['img_focal_length'] = get_focal_length(exif_data)
    dict['img_flash'] = get_flash(exif_data)
    dict['img_shutterspeed'] = get_shutterspeed(exif_data)
    dict['img_exposure_time'] = get_exposure_time(exif_data)

    #pixels, dimensions
    dimensions, total_pixels = get_pixels_dimensions(exif_data)
    dict['img_dimensions'] = dimensions
    dict['img_total_pixels'] = total_pixels

    return dict


def upload_image_extract_metadata_all(dirname, ACCESS_KEY, SECRET_KEY, bucketname):
    ext = ('.jpg', '.jpeg', 'JPG', 'JPEG')

    ls_image = []
    for f in os.listdir(dirname):
        d = os.path.join(dirname, f)
        if os.path.isdir(d):
            cwd = os.getcwd()
            path = os.chdir(d)

            for filename in os.listdir(path):
                if filename.endswith(ext):
                    dict = get_image_metadata(filename)
                    # resizer(os.path.join(cwd, d, filename))

                    sizes = ('', '_small', '_medium')
                    for size in sizes:
                        pic_size = f'{os.path.splitext(filename)[0]}{size}{os.path.splitext(filename)[1]}'
                        url = f'https://{bucketname}.s3.eu-central-1.amazonaws.com/{pic_size}'
                        upload_image_to_aws(pic_size, ACCESS_KEY, SECRET_KEY, bucketname)
                        print(f'{pic_size} uploaded to bucket')

                        if size == '':
                            dict[f'proof_large'] = url
                        else:
                            dict[f'proof{size}'] = url

                    picture_info = AllImage(
                        proof_image_name=dict['proof_image_name'],
                        proof_date=dict['proof_date'],
                        latitude=dict['latitude'],
                        longitude=dict['longitude'],
                        proof_small=dict['proof_small'],
                        proof_medium=dict['proof_medium'],
                        proof_large=dict['proof_large'],
                        batch_key=int(dict['batch_key']),
                    )

                    ls_image.append(picture_info)
                else:
                    continue
            os.chdir(cwd)
    return ls_image


os.getcwd()
