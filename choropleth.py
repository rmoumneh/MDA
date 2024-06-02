import random
import pandas as pd
import json
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import json


color = random.sample(range(0, 43), 43)

municipality_plotly_index_mapping = {
    "Aalst": 0,
    "Antwerp": 1,
    "Arlon": 2,
    "Ath": 3,
    "Bastogne": 4,
    "Brugge": 5,
    "Bruxelles-Capitale - Brussel-Hoofdstad": 6,
    "Charleroi": 7,
    "Dendermonde": 8,
    "Diksmuide": 9,
    "Dinant": 10,
    "Eeklo": 11,
    "Gent": 12,
    "Halle-Vilvoorde": 13,
    "Hasselt": 14,
    "Huy": 15,
    "Ieper": 16,
    "Kortrijk": 17,
    "Leuven": 18,
    "Liège": 19,
    "Maaseik": 20,
    "Marche-en-Famenne": 21,
    "Mechelen": 22,
    "Mons": 23,
    "Mouscron": 24,
    "Namur": 25,
    "Neufchâteau": 26,
    "Nivelles": 27,
    "Oostende": 28,
    "Oudenaarde": 29,
    "Philippeville": 30,
    "Roeselare": 31,
    "Sint-Niklaas": 32,
    "Soignies": 33,
    "Thuin": 34,
    "Tielt": 35,
    "Tongeren": 36,
    "Tournai": 37,
    "Turnhout": 38,
    "Verviers": 39,
    "Veurne": 40,
    "Virton": 41,
    "Waremme": 42,
}

nl_en_mapping = {
    "Aalst": "Alost",
    "Antwerp": "Anvers",
    "Arlon": "Arlon",
    "Ath": "Ath",
    "Bastogne": "Bastogne",
    "Brugge": "Bruges",
    "Bruxelles-Capitale - Brussel-Hoofdstad": "Bruxelles-Capitale",
    "Charleroi": "Charleroi",
    "Dendermonde": "Termonde",
    "Diksmuide": "Dixmude",
    "Dinant": "Dinant",
    "Eeklo": "Eeklo",
    "Gent": "Gand",
    "Halle-Vilvoorde": "Hal-Vilvorde",
    "Hasselt": "Hasselt",
    "Huy": "Huy",
    "Ieper": "Ypres",
    "Kortrijk": "Courtrai",
    "Leuven": "Louvain",
    "Liège": "Liège",
    "Maaseik": "Maaseik",
    "Marche-en-Famenne": "Marche-en-Famenne",
    "Mechelen": "Malines",
    "Mons": "Mons",
    "Mouscron": "Mouscron",
    "Namur": "Namur",
    "Neufchâteau": "Neufchâteau",
    "Nivelles": "Nivelles",
    "Oostende": "Ostende",
    "Oudenaarde": "Audenarde",
    "Philippeville": "Philippeville",
    "Roeselare": "Roulers",
    "Sint-Niklaas": "Saint-Nicolas",
    "Soignies": "Soignies",
    "Thuin": "Thuin",
    "Tielt": "Tielt",
    "Tongeren": "Tongres",
    "Tournai": "Tournai",
    "Turnhout": "Turnhout",
    "Verviers": "Verviers",
    "Veurne": "Furnes",
    "Virton": "Virton",
    "Waremme": "Waremme",
}

inverse_nl_en_mapping = {v: k for k, v in nl_en_mapping.items()}


with open("belgium-with-regions_.geojson", "r") as file:
    geojson = json.load(file)

for i in range(43):
    temp_json = json.loads(json.dumps(geojson["features"][i]["properties"], indent=2))

    name = temp_json["name"]
    municipality_plotly_index_mapping[name] = i

df = pd.read_csv("Survival_data.csv", index_col=0)
df["Survival chance"] = df["Survival chance"].astype(np.float64)
df["Survival chance"] = pd.to_numeric(df["Survival chance"], errors="coerce")
aggregated_df = df.groupby("Arrondisement_NL")["Survival chance"].agg(["mean"])
aggregated_series = aggregated_df.sort_values(by="Arrondisement_NL")["mean"]

aggregated_df.reset_index(drop=False, inplace=True)
aggregated_df.head()

temp_list = []
for idx in range(len(aggregated_df)):
    temp_list.append(
        (
            aggregated_df.iloc[idx, 0],
            inverse_nl_en_mapping[aggregated_df.iloc[idx, 0]],
            aggregated_df.iloc[idx, 1],
        )
    )

df_final = pd.DataFrame(data=temp_list, columns=["nl", "en", "mean"])
df_final.sort_values(by="en", inplace=True)


with open("belgium-with-regions_.geojson", "r") as file:
    geojson = json.load(file)

fig = px.choropleth_mapbox(
    geojson=geojson,
    locations=[feature["properties"]["name"] for feature in geojson["features"]],
    featureidkey="properties.name",
    color=df_final["mean"],
    mapbox_style="carto-positron",
    zoom=7,
    center={"lat": 50.5039, "lon": 4.4699},
    opacity=0.5,
    labels={"color": "Region"},
)

# Update layout for better visualization
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

app = dash.Dash(__name__)
app.layout = html.Div(
    [dcc.Graph(id="choropleth", figure=fig), html.Div(id="output-div")]
)


@app.callback(Output("output-div", "children"), Input("choropleth", "clickData"))
def display_click_data(clickData):
    if clickData is None:
        return "Click anywhere on the map to see the coordinates"
    return html.Div(
        [
            html.H4(str(clickData)),
        ]
    )


fig.update_layout(margin={"r": 15, "t": 15, "l": 15, "b": 15}, height=1000)

if __name__ == "__main__":
    app.run_server(debug=True)
