from create_graph import (
    load_data,
    Objective_function,
    get_list_of_u_nodes,
    get_list_of_v_nodes,
    create_graph,
    merge_degrees_event_count,
)
import argparse
import numpy as np
from sklearn.cluster import DBSCAN
from preprocess import load_data
from utilities import random_coordinates_belgium, add_sampled_cooridnates_to_df
from logger import get_logger
import logging


logger = get_logger(__file__, level=logging.DEBUG)


def main(
    iterations,
    samples_per_iteration=1000,
    eps=0.0001,
    min_samples=3,
    aed_undersample=1000,
    interventions_undersample=4000,
):
    # ---------- Same throughout sampling ---------- #
    aed_df, interventions_df = load_data(root_dir="./data/")
    aed_df = aed_df.sample(aed_undersample)  # TODO
    objective_function = Objective_function(alpha=0.5)

    # ----------- DBSCAN ----------- #

    data_points = (
        interventions_df.loc[:, ["latitude_intervention", "longitude_intervention"]]
        .sample(interventions_undersample)
        .to_numpy()
    )

    db = DBSCAN(eps=eps, min_samples=min_samples, metric="haversine")
    db.fit(np.radians(data_points))

    labels = db.labels_
    unique_labels = set(labels) - {-1}

    cluster_centers = []
    for label in unique_labels:
        class_member_mask = labels == label
        cluster_points = np.array(data_points)[class_member_mask]
        cluster_center = np.mean(cluster_points, axis=0)
        cluster_centers.append(cluster_center)

    logger.info(f"DBSCAN found {len(cluster_centers)} clusters")

    # ------------- same for all iterations ------------- #

    labels, point_counts = np.unique(labels, return_counts=True)
    labels, point_counts = labels[1:], point_counts[1:]  # removing -1 cluster (noise)

    V = get_list_of_v_nodes(
        cluster_centers=cluster_centers, labels=labels, point_counts=point_counts
    )

    # ------------------- Step 0 ------------------- #

    U = get_list_of_u_nodes(df=aed_df)
    G = create_graph(U, V, save_as="graph_init")
    list_of_v_nodes = {
        node for node, data in G.nodes(data=True) if data["bipartite"] == 1
    }
    v_node_degrees = {node: G.degree(node) for node in list_of_v_nodes}
    m = merge_degrees_event_count(V, v_node_degrees)
    loss_0 = objective_function(G, m)

    logger.info(f"Graph initialization (iteration 0) finished")

    # ------------------- sampling  ------------------- #
    best_coordinates = None
    best_loss = loss_0

    for i in range(iterations):
        for j in range(samples_per_iteration):
            latitude_sampled, longitude_sampled = random_coordinates_belgium()
            aed_with_sample_df = add_sampled_cooridnates_to_df(
                df=aed_df,
                id=100000 + j,
                latitude=latitude_sampled,
                longitude=longitude_sampled,  # TODO fix the starting idx for samples
            )
            U = get_list_of_u_nodes(aed_with_sample_df)

            G = create_graph(U, V, save_as=f"graph_{i}_{j}")
            list_of_v_nodes = {
                node for node, data in G.nodes(data=True) if data["bipartite"] == 1
            }
            v_node_degrees = {node: G.degree(node) for node in list_of_v_nodes}
            m = merge_degrees_event_count(V, v_node_degrees)
            loss_iter = objective_function(G, m)

            if loss_iter <= best_loss:
                best_aed = aed_with_sample_df
                best_coordinates = (latitude_sampled, longitude_sampled)
                best_loss = loss_iter
        aed_df = best_aed.copy(deep=True)
        logger.info(
            f"Iteration {i+1} finished with best coordinates: ({best_coordinates[0]},{best_coordinates[1]}) | loss: {best_loss}"
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--iterations",
        type=int,
        required=True,
        help="Number of iterations to run the simluation; equivalent to the number of AEDs to add.",
    )

    parser.add_argument(
        "--samples_per_iteration",
        type=int,
        default=1000,
        help="Defines the sampling count for each iteration",
    )
    parser.add_argument(
        "--eps",
        type=float,
        default=0.0001,
        help="DBSCAN epsilon parameter",
    )
    parser.add_argument(
        "--min_samples",
        type=int,
        default=5,
        help="DBSCAN min_samples parameter for forming clusters",
    )
    parser.add_argument(
        "--aed_undersample",
        type=int,
        default=1000,
        help="Undersample parameter for the aed_df - avoids the app from crashing",
    )

    parser.add_argument(
        "--interventions_undersample",
        type=int,
        default=4000,
        help="Undersample parameter for the interventions_df - avoids the app from crashing",
    )

    args = parser.parse_args()
    main(
        iterations=args.iterations,
        samples_per_iteration=args.samples_per_iteration,
        eps=args.eps,
        min_samples=args.min_samples,
        aed_undersample=args.aed_undersample,
        interventions_undersample=args.interventions_undersample,
    )
