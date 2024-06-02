import random
import pandas as pd

def random_coordinates_belgium():
    # Define the boundaries of Belgium
    min_lat, max_lat = 50.6, 51.5
    min_long, max_long = 2.5, 6.5

    # Generate random latitude and longitude within the boundaries
    latitude = random.uniform(min_lat, max_lat)
    longitude = random.uniform(min_long, max_long)

    return latitude, longitude


def add_sampled_cooridnates_to_df(df, id, latitude, longitude):
    new_row = pd.Series({"id": id, "latitude": latitude, "longitude": longitude})

    df_temp = df.copy(deep=True)
    return pd.concat([df_temp, pd.DataFrame([new_row])], ignore_index=True)

