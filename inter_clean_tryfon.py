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

#############################
### INTERVENTION CLEANING ###
#############################

#### 1. BXL DATA ####

### IMPORT DATA ###

intervb1 = pd.read_parquet('interventions_bxl.parquet.gzip')
intervb2 = pd.read_parquet('interventions_bxl2.parquet.gzip')
interv1 = pd.read_parquet('interventions1.parquet.gzip')
interv2 = pd.read_parquet('interventions2.parquet.gzip')
interv3 = pd.read_parquet('interventions3.parquet.gzip')

### Keep only P003 interventions ###
# P003 - Cardiac arrest
# P039 - Cardiac problem (other than thoracic pain) not taken into account
# Because it doesn't require DEA/AED

i = intervb1[intervb1['eventtype_trip'] != ('P003 - Cardiac arrest')].index
intervb1P003 = intervb1.drop(i)
i = intervb2[intervb2['EventType and EventLevel'] != ('P003  N01 - HARTSTILSTAND - DOOD - OVERLEDEN')].index
intervb2P003 = intervb2.drop(i)

### RENAME FOR STANDARDIZATION ###
intervb1P003.rename(columns={'mission_id':'Mission ID','latitude_permanence':'Latitude permanence',"longitude_permanence":"Longitude permanence",
                             "longitude_intervention":"Longitude intervention","latitude_intervention":"Latitude intervention",
                             "t0":"T0","t1":"T1","t2":"T2","t3":"T3"},inplace=True)
intervb2P003.rename(columns={'Mission ID':'Mission ID','Latitude Permanence':'Latitude permanence',"Longitude Permanence":"Longitude permanence",
                             "Longitude intervention":"Longitude intervention","Latitude intervention":"Latitude intervention",
                             "t0":"T0","t1":"T1","t2":"T2","t3":"T3"},inplace=True)

# print(intervb2P003['Cityname Intervention'].head(5))
### Keep only subset of interest ###
intervb1P003_subset= intervb1P003[['Mission ID','Latitude permanence', 'Longitude permanence','Latitude intervention', 'Longitude intervention','T0', 'T1', 'T2', 'T3']]
intervb2P003_subset= intervb2P003[['Mission ID','Latitude permanence', 'Longitude permanence','Latitude intervention', 'Longitude intervention','T0', 'T1', 'T2', 'T3']]

intervb1P003_subset['PostalCode intervention']= 1000
intervb2P003_subset['PostalCode intervention']= 1000

### CONVERT STANDARDIZED TIME DATA ###

t_lst = ['T0','T1','T2','T3']
for t in (t_lst):
    intervb1P003_subset[t]=intervb1P003_subset.apply(lambda x: nam.time_interv1(x[t]), axis=1)
    i1 = intervb1P003_subset[intervb1P003_subset[t] == date(1, 1, 1)].index
    intervb1P003_subset = intervb1P003_subset.drop(i1)
    intervb2P003_subset[t]=intervb2P003_subset.apply(lambda x: nam.time_interv2(x[t]), axis=1)
    i2 = intervb2P003_subset[intervb2P003_subset[t] == date(1, 1, 1)].index
    intervb2P003_subset = intervb2P003_subset.drop(i2)  

intervb_df =  pd.concat([intervb1P003_subset, intervb2P003_subset])

#### 2. the rest of belgium ####

### IMPORT PACKAGE ###

interv1 = pd.read_parquet('interventions1.parquet.gzip')
interv2 = pd.read_parquet('interventions2.parquet.gzip')
interv3 = pd.read_parquet('interventions3.parquet.gzip')

### Keep only cardiac arrest ###
i = interv1[interv1['EventType Trip'] != ('P003 - Cardiac arrest')].index
interv1P003 = interv1.drop(i)
i = interv2[interv2['EventType Trip'] != ('P003 - Cardiac arrest')].index
interv2P003 = interv2.drop(i)
i = interv3[interv3['EventType Trip'] != ('P003 - Cardiac arrest')].index
interv3P003 = interv3.drop(i)

### Keep only subset of interest ###
interv1P003_subset= interv1P003[['Mission ID','Latitude permanence', 'Longitude permanence','Latitude intervention', 'Longitude intervention','T0', 'T1', 'T2', 'T3','PostalCode intervention']]
interv2P003_subset= interv2P003[['Mission ID','Latitude permanence', 'Longitude permanence','Latitude intervention', 'Longitude intervention','T0', 'T1', 'T2', 'T3','PostalCode intervention']]
interv3P003_subset= interv3P003[['Mission ID','Latitude permanence', 'Longitude permanence','Latitude intervention', 'Longitude intervention','T0', 'T1', 'T2', 'T3','PostalCode intervention']]

### STANDARDIZED TIME DATA ###

t_lst = ['T0','T1']
for t in (t_lst):
    interv1P003_subset[t]=interv1P003_subset.apply(lambda x: nam.time_interv2(x[t]), axis=1)
    i1 = interv1P003_subset[interv1P003_subset[t] == date(1, 1, 1)].index
    interv1P003_subset = interv1P003_subset.drop(i1)
    interv2P003_subset[t]=interv2P003_subset.apply(lambda x: nam.time_interv2(x[t]), axis=1)
    i2 = interv2P003_subset[interv2P003_subset[t] == date(1, 1, 1)].index
    interv2P003_subset = interv2P003_subset.drop(i2)   
    interv3P003_subset[t]=interv3P003_subset.apply(lambda x: nam.time_interv2(x[t]), axis=1)
    i2 = interv3P003_subset[interv3P003_subset[t] == date(1, 1, 1)].index
    interv3P003_subset = interv3P003_subset.drop(i2)  

t_lst2 = ['T2','T3']
for t in (t_lst2):
    interv1P003_subset[t]=interv1P003_subset.apply(lambda x: nam.time_interv3(x[t]), axis=1)
    i1 = interv1P003_subset[interv1P003_subset[t] == date(1, 1, 1)].index
    interv1P003_subset = interv1P003_subset.drop(i1)
    interv2P003_subset[t]=interv2P003_subset.apply(lambda x: nam.time_interv3(x[t]), axis=1)
    i2 = interv2P003_subset[interv2P003_subset[t] == date(1, 1, 1)].index
    interv2P003_subset = interv2P003_subset.drop(i2)   
    interv3P003_subset[t]=interv3P003_subset.apply(lambda x: nam.time_interv3(x[t]), axis=1)
    i2 = interv3P003_subset[interv3P003_subset[t] == date(1, 1, 1)].index
    interv3P003_subset = interv3P003_subset.drop(i2)  

### CONCAT DATA ###
interv_df =  pd.concat([interv1P003_subset, interv2P003_subset, interv2P003_subset])

#### 4. CONCAT BXL ANDS THE REST OF BELGIUM ####

intervALL_df =  pd.concat([interv_df, intervb_df])

#### 5. ADD INTERVENTION TIME COLUMN ####

intervALL_df['Arrival duration'] = intervALL_df.apply( lambda x : nam.arrival_duration(x['T0'],x['T3']), axis=1)

#### -- Save dataframe into csv -- ####
intervb_df.to_csv('Interventions_BXL.csv', index=False)
interv_df.to_csv('Interventions_NOTBXL.csv', index=False)
intervALL_df.to_csv('Interventions_ALL.csv', index=False)