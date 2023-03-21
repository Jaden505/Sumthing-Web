# https://gist.github.com/erans/983821

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Conversion latitude longitude
def decimal_coords(coords, ref):
 decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
 if ref == 'S' or ref == 'W':
     decimal_degrees = -decimal_degrees
 return decimal_degrees

def _convert_to_degrees(dms): 
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    return degrees+minutes+seconds

def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    return None


def get_lat_lon(exif_data):
    
    lat = None
    lon = None

    if "GPSInfo" in exif_data:	
        try:	
            gps_info = exif_data["GPSInfo"]

            gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
            
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = _convert_to_degrees(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat

                lon = _convert_to_degrees(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon
        except:
            return None
    return lat,lon


def get_datetime(exif_data):
    datetime = None

    datetime=exif_data["DateTime"]
    return datetime




