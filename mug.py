#Import package
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import matplotlib
from geopy.distance import geodesic
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from datetime import datetime, timedelta, date
import network_analysis_module as nam

### Import data ###
mug = pd.read_parquet('mug_locations.parquet.gzip')
print(mug.dtypes)
print(len(mug))
print(mug.head())

mug['coordonate'] = mug.apply(lambda x: nam.locationBE('',x['municipality'],x['address_campus']))
# locationBE(numberStr, address, Arrondissement)

print(mug.head())
