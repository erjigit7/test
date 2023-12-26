from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import math

def extract_exif_data(image_path):
    # Open the image
    img = Image.open(image_path)

    # Extract Exif data
    exif_data = img._getexif()
    gps_info = {}
	
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)

            # Check if the tag represents GPS information
            if tag_name == 'GPSInfo':
                
                for gps_tag, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = gps_value
                
	
            # Check if the tag represents DateTime information
            elif tag_name == 'DateTimeOriginal':
                print("DateTime Original:", value)
    return gps_info                
                
	


def get_dji_meta(image_path):
   
    djimeta=["AbsoluteAltitude","RelativeAltitude","GimbalRollDegree","GimbalYawDegree",\
         "GimbalPitchDegree","FlightRollDegree","FlightYawDegree","FlightPitchDegree"]
    
    # read file in binary format and look for XMP metadata portion
    fd = open(image_path,'rb')
    d= fd.read()
    
    xmp_start = d.find(b'<x:xmpmeta')
    xmp_end = d.find(b'</x:xmpmeta')

    # convert bytes to string
    xmp_b = d[xmp_start:xmp_end+12]
    xmp_str = xmp_b.decode()
    
    fd.close()
    
    # parse the XMP string to grab the values
    xmp_dict={}
    for m in djimeta:
        istart = xmp_str.find(m)
        ss=xmp_str[istart:istart+len(m)+10]
        val = float(ss.split('"')[1])
        xmp_dict.update({m : val})
        
    return xmp_dict
    

def convert_gps_to_decimal(gps_info):
    # Extract components of GPS latitude
    degrees_latitude = gps_info.get('GPSLatitude', [0, 0, 0])[0]
    minutes_latitude = gps_info.get('GPSLatitude', [0, 0, 0])[1]
    seconds_latitude = gps_info.get('GPSLatitude', [0, 0, 0])[2]

    # Extract components of GPS longitude
    degrees_longitude = gps_info.get('GPSLongitude', [0, 0, 0])[0]
    minutes_longitude = gps_info.get('GPSLongitude', [0, 0, 0])[1]
    seconds_longitude = gps_info.get('GPSLongitude', [0, 0, 0])[2]

    # Calculate the decimal degree value
    decimal_degrees_latitude = degrees_latitude + minutes_latitude / 60.0 + seconds_latitude / 3600.0
    decimal_degrees_longitude = degrees_longitude + minutes_longitude / 60.0 + seconds_longitude / 3600.0
    
    gps_lat_ref = gps_info.get('GPSLatitudeRef', '')  
    gps_lon_ref = gps_info.get('GPSLongitudeRef', '')
    
    # Check if the latitude is in the Southern Hemisphere (negative)
    if gps_lat_ref == 'S':
        decimal_degrees_latitude = -decimal_degrees_latitude
        
    if gps_lon_ref == 'W':
    	decimal_degrees_longitude = -decimal_degrees_longitude

    return decimal_degrees_latitude, decimal_degrees_longitude
    
    

def calculate_distance(rel_alt, gim_pitch_deg):
    gim_pitch_rad = math.radians(gim_pitch_deg)
    res = rel_alt / math.tan(gim_pitch_rad)
    return math.fabs(res)
        
    
    
def deg_km(earth, radius, lat):
    lat_radian = math.radians(lat)
    min_radius = math.cos(lat_radian) * radius
    
    min_circle = 2 * math.pi * min_radius
    
    min_circle_deg = min_circle / 180
    
    
    return min_circle_deg
    
    
def deg(min_circle_deg, distance):
    dis_kilometr = distance / 1000
    min_deg = dis_kilometr / min_circle_deg
    
    return(min_deg)
    
    
    
image_path = '/home/erjigit/condaProjects/100_0140/DJI_0007.JPG'
exif_data = extract_exif_data(image_path)
dji_data = get_dji_meta(image_path)
lat, lon = convert_gps_to_decimal(exif_data)
rel_alt = dji_data["RelativeAltitude"]
gim_pitch_deg = dji_data["GimbalPitchDegree"]
fli_yaw_deg = dji_data["FlightYawDegree"]
earth = 40075.017
radius = 6371
distance = calculate_distance(rel_alt, gim_pitch_deg)
min_circle_deg = deg_km(earth, radius, lat)
min_deg = deg(min_circle_deg, distance)

print("GPS Latitude (Decimal):", lat,"\nLongitude (Decimal): ", lon, "\nReleativeAltitude: ", rel_alt, "\nGimbalPitchDegree: ", gim_pitch_deg, "\nFlightYawDegree", fli_yaw_deg, "\nDistance to object(m): ", distance)

print("Min Circle: ", min_circle_deg)
print("Min Degree: ", min_deg)
print(  lat - min_deg)
    
    
    
    
    
    
    
    
    
    
