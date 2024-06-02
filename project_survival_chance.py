
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
import network_analysis_module as nam
import requests
import zipfile
import os
import geopandas as gpd
from shapely.geometry import Point, Polygon
import random

########################################
#### COMPUTE MEAN INTERVENTION TIME ####
########################################


#### 1. IMPORT DATA ####
interventionALL_df = pd.read_csv('Interventions_ALL.csv', sep=',')

#### 2. ADD INTERVENTION DISTANCE COLUMN ####

# - Create a new columns'Permance coordonate' [Point] -
#  based on Latitude permanence and Longitude permanence
interventionALL_df['Permanence coordonate'] = interventionALL_df.apply(lambda x: Point(x['Latitude permanence'],
                                                                                        x['Longitude permanence']),
                                                                                        axis=1)

# - Create a new columns 'Intervention coordonate' [Point] -
#  based on Latitude intervention and Longitude intervention
interventionALL_df['Intervention coordonate'] = interventionALL_df.apply(lambda x: Point(x['Latitude intervention'],
                                                                                          x['Longitude intervention']), axis=1)

### Create a new columns 'Distance Intervention in km' [float] ###
#  based on 'Permanence coordonate' and 'Intervention coordonate'
interventionALL_df['Distance Intervention in km'] = interventionALL_df.apply(lambda x: nam.dist(x['Latitude permanence'],
                                                                                             x['Longitude permanence'],
                                                                                             x['Latitude intervention'],
                                                                                             x['Longitude intervention']),
                                                                                             axis=1)

### Remove rows with error for the distance ###
i_neg = interventionALL_df[interventionALL_df['Distance Intervention in km']<0].index
interventionALL_df=interventionALL_df.drop(i_neg)

### 3. COMPUTE Speed per intervention ###

# - Create a new column 'Speed Km/sec' [float] -
# based on 'Distance Intervention in km' and 'Arrival duration'
interventionALL_df['Speed Km/sec'] = interventionALL_df.apply(lambda x: nam.speed(x['Distance Intervention in km'],
                                                                                x['Arrival duration']),
                                                                                axis=1)

# - Remove rows with error for the speed -
i_nan = interventionALL_df[interventionALL_df['Speed Km/sec'].isna()].index
interventionALL_df=interventionALL_df.drop(i_nan)
interventionALL_df['Speed Km/sec'].head(5)


### 4. Calculate Mean speed for arrival time ###
# Speed is computed in km/sec 
mean_speed_kmpsec = interventionALL_df['Speed Km/sec'].mean()
print(mean_speed_kmpsec)

#########################################################
#### CREATE LIST MULTIPOINT FOR AMBULANCE PERMANENCE ####
#########################################################


### IMPORT DATA ###
ambulances_df = pd.read_csv('ambulances.csv', sep=',')

### MULTIPOINT for Nearest Neighbour ###

# 1. Clean a bit more ambulance dataframe
amb_df = ambulances_df[['base','latitude','longitude','Arrondissement']]
# Create a Tuple 'coordonate' from latitude and longitude
amb_df['coordonate'] = list(zip(amb_df.latitude, amb_df.longitude))

# 2. Create a list of coordonate (amb_list) 
# and a Mulitpoint of coordonate (departures)
# for Nearest Neighbour method
amb_list = amb_df['coordonate'].tolist() # TODO into function !!
# print(len(amb_list))
departures= MultiPoint(amb_list)
# print(amb_list[0])
### Create 'PointCoordonate' column ###
# Make to coordonate Tuple into Point
amb_df['PointCoordonate'] = amb_df.apply(lambda x: Point(x['latitude'], x['longitude']), axis=1)
# print(departures)


###################################################
### AED multipoint for Neirest Neighbour method ###
###################################################

### Import data ###
aedCoordonate = pd.read_csv('aedCoordonate.csv', sep=',')

### ADD LATITUDE and LONGITUDE COLUMNS ###

aedCoordonate['Latitude']  = aedCoordonate.apply(lambda x:  nam.latitude_AED(x["('Latitude', 'Longitude')"]), axis=1)
aedCoordonate['Longitude'] = aedCoordonate.apply(lambda x: nam.longitude_AED(x["('Latitude', 'Longitude')"]), axis=1)
aedLocation_df=aedCoordonate[['id','Latitude','Longitude']]
aedLocation_df = aedLocation_df.dropna(how='any')
### AED LOCATIONS ###
# print(aedLocation_df.dtypes)
aedLocation_df['coordonate'] = list(zip(aedLocation_df.Latitude, aedLocation_df.Longitude))
# 2. Create a list of coordonate (AED_list_coord) 
# and a Mulitpoint of coordonate (AED_positions)
# for Nearest Neighbour method
AED_list_coord = aedLocation_df['coordonate'].tolist()
# print(AED_list_coord)
AED_positions = MultiPoint(AED_list_coord)
# print(AED_positions)

###################################
#### SURVIVAL RATE BY POSITION ####
###################################

# print(interventionALL_df.dtypes)

# survival_chance(coordonate, departures, mean_speed_kmpsec, AED_positions)

# From intrvention dataset
# interventionALL_df['Survival Chance'] = interventionALL_df.apply(lambda x: nam.survival_chance((x['Latitude intervention'],x['Longitude intervention']),departures, mean_speed_kmpsec, AED_positions), axis=1)
# print(interventionALL_df['Survival Chance'].head(5))


def datafram_survival_commune(n_point, shapefile_path = 'BELGIUM_Municipalities.shx', name_filpath ='BELGIUM_-_Municipalities.csv'):
    #https://hub.arcgis.com/datasets/9589d9e5e5904f1ea8d245b54f51b4fd/explore
    # shapefile_path = 'BELGIUM_Municipalities.shx'
    municipalities_polygon = gpd.read_file(shapefile_path)
    muni_name = pd.read_csv(name_filpath, sep=',')
    municipality_df = pd.merge(municipalities_polygon, muni_name , left_index=True, right_index=True)

    # NAME_3,VARNAME_3
    df = pd.DataFrame(columns=['Municipality', 'Index', 'Latitude', 'Longitude', 'Survival chance'])
    index = 0
    for polygon in municipality_df['geometry']:
        minx, miny, maxx, maxy = polygon.bounds
        i = 0
        commune = municipality_df['Communes'].iloc[index]
        while i < n_point:
            random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if polygon.contains(random_point):
                i+=1
                lon = random_point.x
                lat = random_point.y
                surv_chance = nam.survival_chance((lat,lon), departures, mean_speed_kmpsec, AED_positions)
                new_row = {'Municipality': commune ,'Index': index, 'Latitude': lat, 'Longitude': lon, 'Survival chance': surv_chance}
                # Inserting the new row
                df.loc[len(df)] = new_row
                # Reset the index
                df = df.reset_index(drop=True) 
        index+=1
        # print(index)
    return df

def datafram_survival_arrond(n_point, shapefile_path = 'BELGIUM_-_Arrondissements.shx', name_filpath ='BELGIUM_-_Arrondissements.csv'):
    #https://hub.arcgis.com/datasets/df9e6a90a6534d83a83589883afff0d8_0/explore?location=50.494149%2C4.492960%2C8.40
    municipalities_polygon = gpd.read_file(shapefile_path)
    muni_name = pd.read_csv(name_filpath, sep=',')
    municipality_df = pd.merge(municipalities_polygon, muni_name , left_index=True, right_index=True)

    # NAME_3,VARNAME_3
    df = pd.DataFrame(columns=['Arrondisement_FR','Arrondisement_NL', 'Index', 'Latitude', 'Longitude', 'Survival chance'])
    index = 0
    for polygon in municipality_df['geometry']:
        minx, miny, maxx, maxy = polygon.bounds
        i = 0
        communeFR = municipality_df['NAME_3'].iloc[index]
        communeNL = municipality_df['VARNAME_3'].iloc[index]
        while i < n_point:
            random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if polygon.contains(random_point):
                i+=1
                lon = random_point.x
                lat = random_point.y
                # print(lat,lon)
                surv_chance = nam.survival_chance((lat,lon), departures, mean_speed_kmpsec, AED_positions)
                new_row = {'Arrondisement_FR': communeFR,'Arrondisement_NL':communeNL ,'Index': index, 'Latitude': lat, 'Longitude': lon, 'Survival chance': surv_chance}
                # Inserting the new row
                df.loc[len(df)] = new_row
                # Reset the index
                df = df.reset_index(drop=True) 
        index+=1
        # print(index)
    return df


shapefile_path_Arr = 'BELGIUM_-_Arrondissements.shx'
shapefile_path_Muni =  'BELGIUM_Municipalities.shx'
name_filpath_Arr = 'BELGIUM_-_Arrondissements.csv'
name_filpath_Muni = 'BELGIUM_-_Municipalities.csv'

dtest = datafram_survival_arrond(100)#,departures, mean_speed_kmpsec, AED_positions)
print(dtest)
# dtest.to_csv('Survival_data100.csv')

