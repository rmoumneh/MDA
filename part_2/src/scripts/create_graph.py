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
import datetime
from typing import List, Tuple, Dict

np.seterr(divide="ignore")

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
directory_path = f"./runs/{timestamp}/"
if not os.path.exists(directory_path):
    os.makedirs(directory_path)


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
    def __init__(self, id, latitude, longitude, events_count) -> None:
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.events_count = events_count
        self._connected_u_nodes = []
        if type == "aed":
            self.range = 1000

    def add_connected_u_node(self, u_node: U_node, distance: float) -> None:
        if u_node not in self._connected_u_nodes and u_node.range >= distance:
            self._connected_u_nodes.append((u_node, distance))

    @property
    def connected_u_nodes(self):
        return self._connected_u_nodes

    @connected_u_nodes.setter
    def connected_u_nodes(self, connected_u_nodes: List[U_node]) -> None:
        self._connected_u_nodes = connected_u_nodes

    def get_edges_for_nx(self):
        return [(self, *u_node_tuple) for u_node_tuple in self.connected_u_nodes]

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.id})"

    def __repr__(self):
        return f"{self.__class__.__name__} (id={self.id}) | (coord=({self.latitude}, {self.longitude})) | (events_count={self.events_count})"


def euclidean_distance(lat0: float, long0: float, lat1: float, long1: float) -> float:
    """

    Args:
        lat0 (float): 
        long0 (float): 
        lat1 (float): 
        long1 (float): 

    Returns:
        float: 
    """
    lat_conversion_factor = 111.32  # km per degree latitude
    long_conversion_factor = (
        40075 * math.cos(math.radians((lat0 + lat1) / 2)) / 360
    )  # km per degree longitude

    dlat = (lat1 - lat0) * lat_conversion_factor
    dlong = (long1 - long0) * long_conversion_factor

    # Euclidean distance in kilometers
    distance = math.sqrt(dlat**2 + dlong**2)

    return distance


def cluster_interventions(
    df: pd.DataFrame,
    eps: float = 0.0001,
    min_samples: int = 3,
    sampled_subset: int = 3000,
    plot_cluster_centers: bool = False,
):
    """

    Args:
        df (pd.DataFrame): 
        eps (float, optional): . Defaults to 0.0001.
        min_samples (int, optional): . Defaults to 3.
        sampled_subset (int, optional): . Defaults to 3000.
        plot_cluster_centers (bool, optional): . Defaults to False.

    Returns:
        _type_: 
    """
    data_points = (
        df.loc[:, ["latitude_intervention", "longitude_intervention"]]
        .sample(sampled_subset)
        .to_numpy()
    )
    db = DBSCAN(eps=eps, min_samples=min_samples, metric="haversine").fit(
        np.radians(data_points)
    )

    # Extract cluster labels
    labels = db.labels_
    unique_labels = set(labels) - {-1}

    cluster_centers = []
    # Compute the centroid of each cluster
    for label in unique_labels:
        class_member_mask = labels == label
        cluster_points = np.array(data_points)[class_member_mask]
        cluster_center = np.mean(cluster_points, axis=0)
        cluster_centers.append(cluster_center)

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

    return (
        cluster_centers,
        labels,
        point_counts,
        data_points,
    )  # Maybe remove "data_points"


def get_list_of_u_nodes(df: pd.DataFrame) -> List[U_node]:  # aed df
    """

    Args:
        df (pd.DataFrame): 

    Returns:
        List[U_node]: 
    """
    U = []
    for _, row in df.iterrows():
        node = U_node(int(row["id"]), row["latitude"], row["longitude"], type="aed")
        U.append(node)

    return U


def get_list_of_v_nodes(
    cluster_centers, labels, point_counts
) -> List[V_node]:  # numpy array output from cluster_interventions
    """

    Args:
        cluster_centers (_type_): 
        labels (_type_): 
        point_counts (_type_): 

    Returns:
        List[V_node]: 
    """
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


def create_graph(U: List[U_node], V: List[V_node], save_as: bool = None) -> nx.Graph:
    """

    Args:
        U (List[U_node]): 
        V (List[V_node]): 
        save_as (bool, optional): . Defaults to None.

    Returns:
        nx.Graph: 
    """

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

    if save_as:
        nx.write_graphml(G, directory_path + f"{save_as}.graphml")

    return G


def merge_degrees_event_count(
    list_of_v_nodes: List[V_node], dict_of_degrees: Dict[V_node, float]
) -> np.ndarray:
    """

    Args:
        list_of_v_nodes (List[V_node]): 
        dict_of_degrees (Dict[V_node, float]): 

    Returns:
        np.ndarray: 
    """
    temp_list = []
    for _, v in enumerate(list_of_v_nodes):
        temp_list.append([dict_of_degrees.get(list_of_v_nodes[v.id]), v.events_count])

    merged_array = np.array(temp_list)  # 2-dim array: in-degree, events_count
    merged_array = merged_array[:, 1] / merged_array[:, 0]
    merged_array[np.isinf(merged_array)] = 999

    return merged_array


class Objective_function:
    def __init__(self, alpha: float):
        self.alpha = alpha

    def __call__(self, G: nx.Graph, count_over_degree: np.ndarray):
        """

        Args:
            G (nx.Graph): 
            count_over_degree (np.ndarray): 

        Returns:
            _type_: 
        """
        total_weight_sum = sum(weight for _, _, weight in G.edges(data="weight"))
        mean_edge_weight = total_weight_sum / G.number_of_edges()
        return (self.alpha * count_over_degree.mean()) + (
            (1 - self.alpha) * mean_edge_weight
        )


def main(aed_df: pd.DataFrame, interventions_df: pd.DataFrame, save_as: bool = "graph"):
    """

    Args:
        aed_df (pd.DataFrame): 
        interventions_df (pd.DataFrame): 
        save_as (bool, optional):  Defaults to "graph".

    Returns:
        _type_: 
    """

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
    aed_df, interventions_df = load_data(root_dir="./data/")
    main(aed_df, interventions_df)
