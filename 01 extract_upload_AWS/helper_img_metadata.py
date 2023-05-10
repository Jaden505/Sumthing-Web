# https://gist.github.com/erans/983821

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


def get_lat_lon_alt(exif_data):
    
    lat = None
    lon = None
    alt = None

    if "GPSInfo" in exif_data:	
        try:	
            gps_info = exif_data["GPSInfo"]

            gps_latitude = _get_if_exist(gps_info, 'GPSLatitude')
            gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
            gps_altitude = _get_if_exist(gps_info, 'GPSAltitude')
            
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = _convert_to_degrees(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat

                lon = _convert_to_degrees(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon
            alt = float(gps_altitude)
        except:
            return None
    return lat,lon,alt


def get_datetime(exif_data):
    datetime = None
    try:
        datetime = exif_data["DateTime"]
    except:
        return None
    return datetime

def get_model(exif_data):
    model = None
    try:
        model = exif_data["Model"] 
        model = model.replace('\x00', '')
        if not isinstance(model, str):
            return None
    except:
        return None
    return model

def get_iso(exif_data):
    iso = None
    try:
        iso = exif_data["ISOSpeedRatings"]
        if not isinstance(iso, int):
            return None        
    except:
        return None
    return iso

def get_f_number(exif_data):
    f_number = None
    try:
        f_number = float(exif_data["FNumber"])
        if not isinstance(f_number, float):
            return None        
    except:
        return None
    return f_number

def get_focal_length(exif_data):
    focal_length = None
    try:
        focal_length = float(exif_data["FocalLength"])
        if not isinstance(focal_length, float):
            return None            
    except:
        return None
    return focal_length

def get_flash(exif_data):
    flash = None
    try:
        flash = exif_data["Flash"]
        if not isinstance(flash, int):
            return None                
    except:
        return None
    return flash

def get_shutterspeed(exif_data):
    shutterspeed = None
    try:
        shutterspeed = float(exif_data["ShutterSpeedValue"])
        if not isinstance(shutterspeed, float):
            return None            
    except:
        return None 
    return shutterspeed

def get_exposure_time(exif_data):
    exposure_time = None
    try:
        exposure_time = float(exif_data["ExposureTime"])
        if not isinstance(exposure_time, float):
            return None                
    except:
        return None
    return exposure_time

def get_pixels_dimensions(exif_data):
    dimensions = None
    total_pixels = None
    try:
        image_width = exif_data["ExifImageWidth"]
        image_height = exif_data["ExifImageHeight"]
        if not isinstance(image_width, int) | isinstance(image_height, int):
            return None, None   
        dimensions = str(image_width) + ' x ' + str(image_height)
        total_pixels = image_width * image_height
    except:
        return None, None
    return dimensions, total_pixels