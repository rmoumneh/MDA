import pyarrow.parquet as pq
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
import math
from sklearn.cluster import DBSCAN
import os


def clean_column_names(df):
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df


def load_data(root_dir):
    aed_dir = root_dir + "raw/aedCoordonate.csv"

    # df = pq.read_table(df)
    aed_df = pd.read_csv(aed_dir)
    aed_df["('Latitude', 'Longitude')"] = aed_df[
        "('Latitude', 'Longitude')"
    ].str.replace(r"[\(\)]", "", regex=True)
    aed_df[["latitude", "longitude"]] = aed_df["('Latitude', 'Longitude')"].str.split(
        ", ", expand=True
    )
    aed_df = clean_column_names(aed_df)
    aed_df["postal_code"] = aed_df["postal_code"].astype("Int64")
    aed_df["latitude"] = aed_df["latitude"].astype(np.float64)
    aed_df["longitude"] = aed_df["longitude"].astype(np.float64)
    aed_df.columns = aed_df.columns.str.lower()
    aed_df.head()

    aed_df = aed_df.loc[
        :,
        [
            "id",
            "type",
            "address",
            "number",
            "postal_code",
            "municipality",
            "province",
            "public",
            "available",
            "hours",
            "latitude",
            "longitude",
        ],
    ]
    aed_df.dropna(subset=["id", "latitude", "longitude"], inplace=True)

    # Specify the directory path
    directory = root_dir + "raw/interventions"

    list_of_file_directories = []
    for filename in os.listdir(directory):
        if filename.endswith(".parquet.gzip"):
            list_of_file_directories.append(root_dir + "raw/interventions/" + filename)

    interventions_df = pq.read_table(list_of_file_directories)
    interventions_df = interventions_df.to_pandas()
    interventions_df = clean_column_names(interventions_df)

    try:
        interventions_df = interventions_df.rename(
            columns={"eventtype_and_eventlevel": "eventtype_trip"}
        )
    except KeyError:
        interventions_df.dropna(subset=["eventtype_and_eventlevel"], inplace=True)
    interventions_df = clean_column_names(interventions_df)

    interventions_df.dropna(subset=["eventtype_trip"], inplace=True)
    interventions_df = interventions_df.loc[
        interventions_df["eventtype_trip"].str.contains("P003"), :
    ]

    min_lat = 49.5
    max_lat = 51.5
    min_long = 2.5
    max_long = 6.5

    interventions_df = interventions_df[
        (interventions_df["latitude_intervention"] >= min_lat)
        & (interventions_df["latitude_intervention"] <= max_lat)
    ]
    interventions_df = interventions_df[
        (interventions_df["longitude_intervention"] >= min_long)
        & (interventions_df["longitude_intervention"] <= max_long)
    ]
    interventions_df = interventions_df[
        (interventions_df["eventtype_trip"].str.contains("P003"))
    ]

    interventions_df = interventions_df.dropna(subset=["latitude_intervention"])
    interventions_df = interventions_df.dropna(subset=["longitude_intervention"])

    return aed_df, interventions_df
