import requests
import zipfile
import geopandas as gpd
import pandas as pd
import os


shapefile_path = 'BELGIUM_Municipalities.shx' #https://hub.arcgis.com/datasets/9589d9e5e5904f1ea8d245b54f51b4fd/explore
municipalities_polygon = gpd.read_file(shapefile_path)
muni_name = pd.read_csv('BELGIUM_-_Municipalities.csv', sep=',')
print(muni_name.columns)
municipality_df = pd.merge(municipalities_polygon, muni_name , left_index=True, right_index=True)
print(municipality_df.head())


import geopandas as gpd
from shapely.geometry import Point, Polygon
import random

df = pd.DataFrame(columns=['Municipality', 'Index', 'Latitude', 'Longitude', 'Survival chance'])
index = 0
n_point = 1
for polygon in municipality_df['geometry']:
    minx, miny, maxx, maxy = polygon.bounds
    # municipalty_name = 
    i = 0
    commune = municipality_df['Communes'].iloc[index]
    while i < n_point:
        random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(random_point):
            i+=1
            lat = random_point.x
            lon = random_point.y
            surv_chance = i #survival_chance((lat,lon), departures, mean_speed_kmpsec, AED_positions)
            new_row = {'Municipality': commune ,'Index': index, 'Latitude': lat, 'Longitude': lon, 'Survival chance': surv_chance}
            # Inserting the new row
            df.loc[len(df)] = new_row
            # Reset the index
            df = df.reset_index(drop=True) 
    index+=1
    print(index)

print(df)

shapefile_path = 'BELGIUM_Municipalities.shx' #https://hub.arcgis.com/datasets/9589d9e5e5904f1ea8d245b54f51b4fd/explore
municipalities_polygon = gpd.read_file(shapefile_path)
muni_name = pd.read_csv('BELGIUM_-_Municipalities.csv', sep=',')
municipality_df = pd.merge(municipalities_polygon, muni_name , left_index=True, right_index=True)

def datafram_survival(n_point, shapefile_path = 'BELGIUM_Municipalities.shx', name_filpath ='BELGIUM_-_Municipalities.csv'):
    #https://hub.arcgis.com/datasets/9589d9e5e5904f1ea8d245b54f51b4fd/explore
    # shapefile_path = 'BELGIUM_Municipalities.shx'
    municipalities_polygon = gpd.read_file(shapefile_path)
    muni_name = pd.read_csv(name_filpath, sep=',')
    municipality_df = pd.merge(municipalities_polygon, muni_name , left_index=True, right_index=True)

    df = pd.DataFrame(columns=['Municipality', 'Index', 'Latitude', 'Longitude', 'Survival chance'])
    index = 0
    n_point = 1
    for polygon in municipality_df['geometry']:
        minx, miny, maxx, maxy = polygon.bounds
        # municipalty_name = 
        i = 0
        commune = municipality_df['Communes'].iloc[index]
        while i < n_point:
            random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if polygon.contains(random_point):
                i+=1
                lat = random_point.x
                lon = random_point.y
                surv_chance = i #survival_chance((lat,lon), departures, mean_speed_kmpsec, AED_positions)
                new_row = {'Municipality': commune ,'Index': index, 'Latitude': lat, 'Longitude': lon, 'Survival chance': surv_chance}
                # Inserting the new row
                df.loc[len(df)] = new_row
                # Reset the index
                df = df.reset_index(drop=True) 
        index+=1
        print(index)
    return df

dtest = datafram_survival(1)
print(dtest)
# print(df.head())


# def generate_random_points(polygon, num_points):
#     points = []
#     minx, miny, maxx, maxy = polygon.bounds
#     while len(points) < num_points:
#         random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
#         if polygon.contains(random_point):
#             points.append(random_point)
#     return points


# def generate_points_by_municipality(shapefile_path, num_points_per_municipality):
#     municipalities = gpd.read_file(shapefile_path)
#     all_points = {}
    
#     for index, row in municipalities.iterrows():
#         municipality_name = row['name']  # Assurez-vous que le champ 'name' existe dans votre shapefile
#         polygon = row['geometry']
#         points = generate_random_points(polygon, num_points_per_municipality)
#         all_points[municipality_name] = points
    
#     return all_points
