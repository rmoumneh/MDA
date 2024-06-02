import pyarrow.parquet as pq
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
import math
from sklearn.cluster import DBSCAN
import os
from preprocess import load_data


np.seterr(divide="ignore")


class U_node:
    def __init__(self, id, latitude, longitude, type="aed"):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.type = type

        if type == "aed":
            self.range = 20  # in km | is used in eucledean coordinates

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.id})"

    def __repr__(self):
        return f"{self.__class__.__name__} (id={self.id}) | (coord=({self.latitude}, {self.longitude}))"


class V_node:
    def __init__(self, id, latitude, longitude, events_count):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.events_count = events_count
        self._connected_u_nodes = []
        if type == "aed":
            self.range = 1000

    def add_connected_u_node(self, u_node, distance):
        if u_node not in self._connected_u_nodes and u_node.range >= distance:
            self._connected_u_nodes.append((u_node, distance))

    @property
    def connected_u_nodes(self):
        return self._connected_u_nodes

    @connected_u_nodes.setter
    def connected_u_nodes(self, connected_u_nodes):
        self._connected_u_nodes = connected_u_nodes

    def get_edges_for_nx(self):
        return [(self, *u_node_tuple) for u_node_tuple in self.connected_u_nodes]

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.id})"

    def __repr__(self):
        return f"{self.__class__.__name__} (id={self.id}) | (coord=({self.latitude}, {self.longitude})) | (events_count={self.events_count})"


def euclidean_distance(lat0, long0, lat1, long1):

    lat_conversion_factor = 111.32  # km per degree latitude
    long_conversion_factor = (
        40075 * math.cos(math.radians((lat0 + lat1) / 2)) / 360
    )  # km per degree longitude

    # Convert latitude and longitude differences to kilometers
    dlat = (lat1 - lat0) * lat_conversion_factor
    dlong = (long1 - long0) * long_conversion_factor

    # Euclidean distance in kilometers
    distance = math.sqrt(dlat**2 + dlong**2)

    return distance


def cluster_interventions(
    df, eps=0.0001, min_samples=3, sampled_subset=3000, plot_cluster_centers=False
):
    data_points = (
        df.loc[:, ["latitude_intervention", "longitude_intervention"]]
        .sample(sampled_subset)
        .to_numpy()
    )
    print(f"data_points shape: {data_points}")
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='haversine').fit(np.radians(data_points))

    # Extract cluster labels
    labels = db.labels_
    unique_labels = set(labels) - {-1}

    cluster_centers = []
    # Compute the centroid of each cluster
    for label in unique_labels:
        class_member_mask = (labels == label)
        cluster_points = np.array(data_points)[class_member_mask]
        cluster_center = np.mean(cluster_points, axis=0)
        cluster_centers.append(cluster_center)
        
    print(f"class_member_mask shape: {class_member_mask}")
    labels, point_counts = np.unique(labels, return_counts=True)
    labels, point_counts = labels[1:], point_counts[1:]  # removing -1 cluster (noise)

    if plot_cluster_centers:

        plt.figure(figsize=(10, 8))
        for cluster_center in cluster_centers:
            plt.plot(
                cluster_center[1],
                cluster_center[0],
                ".",
                markerfacecolor="black",
                markeredgecolor="k",
                markersize=10,
            )

        plt.title("Cluster Centers")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.show()
        
    print(f"DBSCAN found: {len(cluster_centers)} clusters")
    return (
        cluster_centers,
        labels,
        point_counts,
        data_points,
    )  # Maybe remove "data_points"


def get_list_of_u_nodes(df):  # aed df
    U = []
    for _, row in df.iterrows():
        node = U_node(int(row["id"]), row["latitude"], row["longitude"], type="aed")
        U.append(node)

    return U


def get_list_of_v_nodes(
    cluster_centers, labels, point_counts
):  # numpy array output from cluster_interventions
    V = []
    for idx, current_label in enumerate(labels):
        node = V_node(
            id=current_label,
            latitude=cluster_centers[idx][0],
            longitude=cluster_centers[idx][1],
            events_count=point_counts[idx],
        )
        V.append(node)

    return V


def create_graph(U, V, save_graph=None):

    G = nx.Graph()
    G.add_nodes_from(U, bipartite=0)
    G.add_nodes_from(V, bipartite=1)

    edges = []
    for u_node in U:
        for v_node in V:
            distance = euclidean_distance(
                u_node.latitude,
                u_node.longitude,
                v_node.latitude,
                v_node.longitude,
            )

            v_node.add_connected_u_node(u_node, distance)

            if u_node.range >= distance:
                edges.append((v_node, u_node, distance))
            # edges += v_node.get_edges_for_nx()

    G.add_weighted_edges_from(edges)

    if save_graph:
        nx.write_graphml(G, f"{save_graph}.graphml")  # TODO
        nx.write_gexf(G, f"{save_graph}.gexf")

    return G


def merge_degrees_event_count(list_of_v_nodes, dict_of_degrees):
    temp_list = []
    for _, v in enumerate(list_of_v_nodes):
        temp_list.append([dict_of_degrees.get(list_of_v_nodes[v.id]), v.events_count])

    merged_array = np.array(temp_list)  # 2-dim array: in-degree, events_count
    merged_array = merged_array[:, 1] / merged_array[:, 0]
    merged_array[np.isinf(merged_array)] = 999

    return merged_array


class Objective_function:
    def __init__(self, alpha):
        self.alpha = alpha

    def __call__(self, G, count_over_degree):
        total_weight_sum = sum(weight for _, _, weight in G.edges(data="weight"))
        mean_edge_weight = total_weight_sum / G.number_of_edges()
        return (self.alpha * count_over_degree.mean()) + (
            (1 - self.alpha) * mean_edge_weight
        )


def main(aed_df, interventions_df, save_as="graph"):

    objective_function = Objective_function(alpha=0.5)
    cluster_centers, labels, point_counts = cluster_interventions(interventions_df)
    U = get_list_of_u_nodes(aed_df)
    V = get_list_of_v_nodes(cluster_centers, labels, point_counts)

    G = create_graph(U, V, save_as)
    list_of_v_nodes = {
        node for node, data in G.nodes(data=True) if data["bipartite"] == 1
    }
    v_node_degrees = {node: G.degree(node) for node in list_of_v_nodes}
    m = merge_degrees_event_count(V, v_node_degrees)

    return objective_function(G, m)


if __name__ == "__main__":
    aed_df, interventions_df = load_data(root_dir="../../data/")
    print(main(aed_df, interventions_df))
