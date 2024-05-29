#Import package
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import matplotlib
from geopy.distance import geodesic
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from datetime import datetime, timedelta, date
import math


# ADD LOCATION COORDONATE TO AED DATAFRAME
# using geopy library and Nominatim class object
# NOTE: Take long times to run (~10 min for 160 demands !)
# Good practice to save dataframe into table !

# from geopy.geocoders import Nominatim
def locationBE(numberStr, address, Arrondissement):
    """
    Convert address into coordonate

    Input : 
        numberStr = number of house on the street [string],
        address = name of the street [string],
        Arrondissement = municipality [string]

    Output:
        latitude,longitude [float,float]
    """
    try:
        geolocator = Nominatim(user_agent="my_user_agent")
        street = numberStr+' '+address
        city = Arrondissement
        country = 'Belgique'
        loc = geolocator.geocode(street+','+city+','+ country, timeout=120)
        return loc.latitude,loc.longitude
    except:
        return float('nan'),float('nan')

# Testing locationBE function
# lat,lon = locationBE('1','Albert Leemansplein','Bruxelles')
# print(lat)


def latitude_AED(coordonate_string):
    """
    Return the latitude float of a string fomrat coordonate '(latitude,longitude)'

    Input : 
        coordonate_string = string format of coordonate (latitude_float,longitude_float) [string] 
    
    Output: 
        latitude_float = float number of the latitude [float]
    
    """
    coord_str = coordonate_string.replace('(','')
    coord_str = coord_str.replace(')','')
    latitude, longitude = coord_str.split(',')
    if latitude=='nan':
        latitude_float = float('nan')
    else:
        latitude_float = float(latitude)
    # longitude_float = float(longitude)
    return latitude_float

def longitude_AED(coordonate_string):
    """
    Return the longitude float of a string fomrat coordonate '(latitude,longitude)'
    
    Input : 
        coordonate_string = string format of coordonate (latitude_float,longitude_float) [string] 
    
    Output: 
        longitude_float = float number of the longitude [float]
    
    """
    coord_str = coordonate_string.replace('(','')
    coord_str = coord_str.replace(')','')
    latitude, longitude = coord_str.split(',')
    # latitude_float = float(latitude)
    longitude_float = float(longitude)
    return longitude_float


# Function Distance parcoure
# from geopy.distance import geodesic
def dist(Lat_per,Lon_per, lat_desti, long_desti):
    """
    Return distance between 

    Input:
        Lat_per = latitude of permanence [float],
        Lon_per = longitude of permanence [float],
        lat_desti = latitude of intervention [float],
        long_desti = latitude of intervention [float]
    Outpot:
        distance in km [float]
    """
    # print(geodesic((Lat_per,Lon_per), (lat_desti, long_desti)).km)
    # print(geodesic((Lat_per,Lon_per), (lat_desti, long_desti)))
    try:
        dist_km = geodesic((Lat_per,Lon_per), (lat_desti, long_desti)).km
    except:
        dist_km = -10 #negative number to easily treat(remove) it
        # TO correct ! 
        # dist_km = Point(-100.0,-100.0)
    return dist_km


# Function speed per intervention
def speed(distance_km,time_sec):
    """
    Return the speed of arrival at the intervention location

    Input:
        distance_km = distance in km betweent the permanence and the intervention locations [float]
        time_sec = time in seconds between the start of the operator call and the arrival of the ambulance at the intervention location [float]
    Output:
        mean speed of the travel in km per sec [float] 

    """
    try:
        speed_Km_per_sec = distance_km/time_sec
    except:
        speed_Km_per_sec = float("nan")
        # print('Time equal 0')
    return speed_Km_per_sec

# Function to convert point data into coordonates

def convert_point_to_coordonate(point):
    """
    Convert point type data into coordonates

    Input:
        point = Point type coordonate data [Point]
    
    Output:
        Tuple of latitude and longitude [(float,float)] 
    """
    pstr = str(point)
    pstr = pstr.replace('POINT (','')
    pstr = pstr.replace(')','')
    lat,lon = pstr.split(' ')
    coord = (float(lat),float(lon))
    return coord

def time_for_intervention(coordonate, departures, mean_speed_kmpsec):
    """
    Return the time required for intervention at the location depending on the permanence location

    Input:
        coordonate = coordonate of intervention locaiton (latitude,longitude) [Tuple]
        departures = Multipoint of all permanence locations [Multipoint]
        mean_speed_kmpsec = speed to arrive at the location [float]

    Output:
        time in seconds of the arrival time [float]
    """
    coord_point = Point(coordonate)
    nearest_depart = nearest_points(coord_point, departures)
    coord_amb = convert_point_to_coordonate(nearest_depart[1])
    distance_km = geodesic(coord_amb,coordonate).km
    time_sec = distance_km/mean_speed_kmpsec

    return time_sec

def AED_access(coordonate, AED_positions):
    """
    Return the distance of the nearest AED devices 
    and a boolean if the nearest DEA is closer than 100 m

    Input : 
    coordonate = coordonate of intervention locaiton (latitude,longitude) [Tuple]
    AED_positions = Multipoint of all AED locations [Multipoint]

    Ouput :
        distance_AED = distance in km of the nearest AED
        access = True if nearest AED is close [Boolean]
    """
    coord_point = Point(coordonate)
    nearest_AED = nearest_points(coord_point, AED_positions)
    coord_AED = convert_point_to_coordonate(nearest_AED[1])
    distance_AED = geodesic(coord_AED, coordonate).km
    if distance_AED <= 0.1: #less than 100 m
        access = True
    else:
        access = False
    return distance_AED, access

# Survival chance function 

# Au-delà de 3 minutes d’arrêt cardiaque, les chances de survies diminuent de 10% chaque minute !
# Après la crise, chaque minute sans prise en charge diminue de 10% les chances de survie de la victime. 
# Au-delà de 5 minutes d’arrêt du cœur,les lésions cérébrales sont irréversibles. Au-delà de 12 minutes, c’est la mort
# Le taux de survie en cas de défibrillation immédiate est de 75%

def survival_chance(coordonate):
    """
    Return survival chance in percent if a cardiac arrest occurs at the coordonate location

    Input : 
        coordonate = coordonate of intervention locaiton (latitude,longitude) [Tuple]
    Output : 
        survival chance in percent
    """
    time_interv = time_for_intervention(coordonate) #in seconds
    distance_AED, access = AED_access(coordonate) # in km
    human_walk = 5/(3600) # in km/sec (equivalent to 5 km/heure)
    initial_survival = 90 # % chance of survival, see https://sofia.medicalistes.fr/spip/spip.php?article174
    if access:
        time_AED = (distance_AED/human_walk)
        decrease_survival_chance = (time_AED/60)*10
    else:
        # Golden rule
        decrease_survival_chance = (time_interv/60)*10 #minus 10% chance of survive eery 10 minutes
    survival = initial_survival - decrease_survival_chance
    if survival <= 0:
        return 0
    else:
        return survival
    
    