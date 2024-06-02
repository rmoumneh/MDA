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


###################
### POSTAL CODE ###
###################

### Import data ###
postal_codes = pd.read_parquet('PostalCodesBE .parquet')

### Cleaining Postal Code ###
postal_codes.head()
for index, value in postal_codes.iterrows():
    if postal_codes.at[index,'reg_name_fr'] == 'Région flamande':
        postal_codes.at[index,'Region'] = 'Flanders'
        postal_codes.at[index,'Province'] = postal_codes.at[index,'prov_name_nl']
        postal_codes.at[index,'Arrondissement'] = postal_codes.at[index,'arr_name_nl']
        postal_codes.at[index,'Municipality'] = postal_codes.at[index,'mun_name_nl']
    elif postal_codes.at[index,'reg_name_fr'] == 'Région wallonne':
        postal_codes.at[index,'Region'] = 'Wallonia'
        postal_codes.at[index,'Province'] = postal_codes.at[index,'prov_name_fr']
        postal_codes.at[index,'Arrondissement'] = postal_codes.at[index,'arr_name_fr']
        postal_codes.at[index,'Municipality'] = postal_codes.at[index,'mun_name_fr']
    elif postal_codes.at[index,'reg_name_fr'] == 'Région de Bruxelles-Capitale':
        postal_codes.at[index,'Region'] = 'Brussels'
        postal_codes.at[index,'Province'] = postal_codes.at[index,'prov_name_fr']
        postal_codes.at[index,'Arrondissement'] = postal_codes.at[index,'arr_name_fr']
        postal_codes.at[index,'Municipality'] = postal_codes.at[index,'mun_name_fr']
    else:
        postal_codes.at[index,'Region'] = 'None'
        postal_codes.at[index,'Province'] = 'None'
        postal_codes.at[index,'Arrondissement'] = 'None'
        postal_codes.at[index,'Municipality'] = 'None'

for a, b in zip(postal_codes.columns, range(0,len(postal_codes.columns))):
                print(f'{a}, column number {b}')
postal_codes_subset = postal_codes.iloc[:,[2,4,5,6,7,8,26,27,28,29]]
postal_codes_subset.head()

postal_codes_subset = postal_codes.iloc[:,[2,4,5,6,7,8,26,27,28,29]]

### Save the datatable ###
postal_codes_subset.to_csv('postal_codes.csv', index=False)

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

# print(intervALL_df.head())




#############################
### AMBULANCE CLEANING ###
#############################

### IMPORT DATA ###

ambulances = pd.read_parquet('ambulance_locations.parquet.gzip')
postal_codes_subset = pd.read_csv('postal_codes.csv', sep=',')

### COMBINE AMBULANCE AND POSTAL CODE ###
ambulances_cl=ambulances.copy()
regions = {'Brussels Hoofdstedelijk Gewest':'Brussels','Vlaams Gewest':'Flanders','Waals Gewest':'Wallonia','null':'null'}
ambulances_cl['region']=ambulances_cl['region'].map(regions)

for column in ambulances_cl.columns:
    if ambulances_cl[column].dtype=='str':
        ambulances_cl[column]=ambulances_cl[column].str.title().str.strip()
    else:
        ambulances_cl[column]=ambulances_cl[column]      
  
for index, row in ambulances_cl.iterrows():
    item = row['departure_location']
    strings = item.split()
    ambulances_cl.at[index,'departure_municipality']=item.split()[-1].title()
    for string in strings:
        if (len(string) == 4) and (string.isdigit()):
            ambulances_cl.at[index, 'departure_postalcode'] = string    

ambulances_cl['departure_postalcode'] = ambulances_cl.apply(lambda x: int(x['departure_postalcode']), axis=1)

ambulances_all = pd.merge(ambulances_cl,postal_codes_subset, left_on = 'departure_postalcode', right_on = 'postcode', how ='left')
for a, b in zip(ambulances_all.columns, range(0,len(ambulances_all.columns))):
                print(f'{a}, column number {b}')

ambulances_subset = ambulances_all.iloc[:,[0,2,3,4,5,6,7,9,10,17,18,19]]

### SAVE THE DATA ###
ambulances_subset.to_csv('ambulances.csv', index=False)

######################
#### AED CLEANING ####
######################

### IMPORT DATA ###
aed = pd.read_parquet('aed_locations.parquet.gzip')
aed_cl=aed.copy()

### 1. FIrst Cleaning ###

for column in aed_cl.columns:
    if aed_cl[column].dtype=='object':
        aed_cl[column]=aed_cl[column].str.title().str.strip()
    else:
        aed_cl[column]=aed_cl[column]    

aed_cl.loc[aed_cl['type'].isin(['Appareil fixe','Appareil Fixe','Appareil fixe-Vast apparaat','Vast apparaat','Vast apparaat']),'type']='Fixed'
aed_cl.loc[aed_cl['type'].isin(['Appareil Mobile- Mobiel apparaat','M5066A']),'type']='Mobile'

aed_cl['postal_code']=aed_cl['postal_code'].astype('str').str.replace('.0','')

for index, value in aed.iterrows():
    if aed_cl.iloc[index, 8] in ['J', 'Ja', 'Oui', 'Oui-Ja', 'y', 'Y']:
        aed_cl.loc[index, 'public'] = 'Yes'
    elif aed_cl.iloc[index, 8] in ['Non-Nee', 'N', 'Nee']:
        aed_cl.loc[index, 'public'] = 'No'
    else:
        aed_cl.iloc[index, 8] = 'None'
        
for index, value in aed.iterrows():
    if aed_cl.iloc[index, 9] in ['J', 'Ja', 'Oui', 'Oui-Ja', 'y', 'Y', 'oui via interphone','Accessible par toute personne présente dans l inrfastructure.','Oui-Ja "Niet tijdens activiteiten van de wielervrienden"']:
        aed_cl.loc[index, 'available'] = 'Yes'
    elif aed_cl.iloc[index, 9] in ['Non-Nee', 'N', 'Nee']:
        aed_cl.loc[index, 'available'] = 'No'
    elif aed_cl.iloc[index, 9] in ['09.00 - 17.00', '9.00 - 17.00', 'Nee']:
        aed_cl.loc[index, 'available'] = '09.00 - 17.00'
    elif aed_cl.iloc[index, 9] in ['09u-12u en op aanvraag']:
        aed_cl.loc[index, 'available'] = '09.00 - 12.00'
    elif aed_cl.iloc[index, 9] in ['5h00 à 25h00', 'de 5h00 à 25h00']:
        aed_cl.loc[index, 'available'] = '05.00 - 23.59'
    elif aed_cl.iloc[index, 9] in ['8:00 - 17:00', 'N', 'Nee']:
        aed_cl.loc[index, 'available'] = '8:00 - 17:00'
    elif aed_cl.iloc[index, 9] in ['16u-23u tijdens opening sporthal']:
        aed_cl.loc[index, 'available'] = '16.00 - 23.00'
    elif aed_cl.iloc[index, 9] in ['De 5h30 à 21h30']:
        aed_cl.loc[index, 'available'] = '05.30 - 21.30'
    elif aed_cl.iloc[index, 9] in ['Dispo 24/7 - sauf samedi de 12h à dimanche 20h', 'Dispo. tout le temps sauf du samedi midi au dimanche 21h']:
        aed_cl.loc[index, 'available'] = '00.00 - 23.59'
    elif aed_cl.iloc[index, 9] in ['Heure de bureau en semaine', 'Heures de bureau', 'Horaire d ouverture de la buvette','Pendant heures d ouverture du site',
                                   'Pendant les heures de cours','Tijdens de kantooruren','Tijdens kantooruren','Tijdens openingsuren van het museum','enkel tijdens kantooruren',
                                   'enkel tijdens de kantooruren (8 - 19u)','horaire d ouverture de la pharmacie','indien de site open is, volledig toegangkelijk','kantooruren',
                                   'selon heures d ouverture d Euro-Délices','tijdens de kantooruren','tijdens de kantooruren in de week','tijdens de openingsuren','tijdens de werkuren',
                                   'tijdens onze openingsuren, zie nr. 12','tijdens openinguren sportcentrum','tijdens werkuren','zie rooster','Heures de bureau ']:
        aed_cl.loc[index, 'available'] = 'Working Opening Time'
    elif aed_cl.iloc[index, 9] in ['maandag, dinsdag, donderdag, vrijdag', 'du lundi au vendredi ']: 
        aed_cl.loc[index, 'available'] = 'During Weekdays'
    else:
        aed_cl.iloc[index, 9] = 'None'  

### MERGE AED and POSTAL CODE ###

aed_cl['postal_code'] = aed_cl.apply(lambda x: float(x['postal_code']), axis=1)

aed_all = pd.merge(aed_cl,postal_codes_subset, left_on = 'postal_code', right_on = 'postcode', how ='left')
for a, b in zip(aed_all.columns, range(0,len(aed_all.columns))):
                print(f'{a}, column number {b}')

aed_subset = aed_all.iloc[:,[0,1,2,3,17,18,19,20,1,4,8,9,10]]

### SAVE FIRST DATASET ###
aed_subset.to_csv('aed.csv', index=False)

#### 2. 

### IMPORT DATA ###

aed_df = pd.read_csv('aed.csv', sep=',')

### TRANSFORM ADDRESS TO COORDONATE
aed_df['numberStr'] = aed_df['number'].apply(nam.streetnumber)
max = len(aed_df)
n = max/166 # 166 is arbitrary, around 10 minutes per part

for i in range(1, 45):
    aedpart_df=aed_df.loc[(i*166):(i+1)*166]
    aedpart_df['Latitude','Longitude'] = aedpart_df.apply(lambda x: nam.locationBE(x['numberStr'], x['address'], x['Arrondissement']), axis=1)
    aedpart_df.to_csv('aedOK'+str(i)+'.csv', index=False)

# Remove data from part 42 to 46 due to issue with geopy
# There is an issue with data from head(42 to 44)

for i in range(45, n):
    aedpart_df=aed_df.loc[(i*166):(i+1)*166]
    aedpart_df['Latitude','Longitude'] = aedpart_df.apply(lambda x: nam.locationBE(x['numberStr'], x['address'], x['Arrondissement']), axis=1)
    aedpart_df.to_csv('aedOK'+str(i)+'.csv', index=False)

# concate the part togheter
aed_list = []
for i in range(106): #I remove the 165 because
    if i >= 42 and i <=44:
        continue
    else:
        exec("aedOK"+str(i)+"_df = pd.read_csv('aedOK"+str(i)+".csv', sep=',')")
        eval("aed_list.append(aedOK"+str(i)+"_df)")

aedCoordonate = pd.concat(aed_list)

### SAVE DATA ###
aedCoordonate.to_csv('aedCoordonate.csv', index=False)



