import hashlib, math
from PIL import Image, ImageStat


def get_hash(img_path):
    # This function will return the md5 checksum for any input image.
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()


def find_mean(imgPath):
    try:
        img = Image.open(imgPath)
        return ImageStat.Stat(img).mean
    except:
        print("could not open file, moving on")


def within_one_meter(lat1, lon1, lat2, lon2):
    # convert coordinates to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = 6371 * c * 1000  # multiply by radius of Earth (in meters)

    return distance <= 1


def check_within_one_meter(lat_lon_pairs, target_lat, target_lon):
    for lat, lon in lat_lon_pairs:
        if within_one_meter(lat, lon, target_lat, target_lon):
            return True
    return False
