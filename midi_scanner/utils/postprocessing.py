from typing import List, Tuple
from music21 import stream, meter, key, metadata, converter, clef
import music21 as music21
from midi_scanner.PlayedNote import PlayedNote

from sklearn.cluster import KMeans
from kneed import KneeLocator
from matplotlib import pyplot as plt

from midi_scanner.utils.ColorMidiScanner import MidiScannerColor, ColorFormat

from typing import List

import numpy as np
from numpy.typing import ArrayLike

import logging
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from scipy.spatial.distance import cdist

import cv2


__postprocessing_logger = logging.getLogger("Postprocessing")

def get_clusters(note_list):

    notes_nb_frames = [note.nb_frame for note in note_list]

    X = np.array(notes_nb_frames).reshape(-1,1)
    kmeans_kwargs = {
        #"init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 42,
    }

    sse = []
    for k in range(1, 9):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(X)
        sse.append(kmeans.inertia_)

    plt.plot(range(1,9), sse)
    plt.show()

    # we assume inertia is going down 
    
    baseline = sse[0]
    previous = sse[0]
    nb_cluster_optim = 0
    for i, inertia in enumerate(sse[1:]):
        drop = (previous - inertia ) / baseline
        __postprocessing_logger.debug(f"Drop: [{drop}]")
        if drop < 0.01:
            nb_cluster_optim = i + 1
            break
        previous = inertia
    else:
        nb_cluster_optim = len(sse)
        __postprocessing_logger.warning("Did not find optimum number of clusters")

    __postprocessing_logger.debug(f"Inertias : [{sse}]")
    __postprocessing_logger.info(f"Using [{nb_cluster_optim}] clusters")

    kl = KneeLocator(
        range(1,9), sse, curve="convex", direction="decreasing"
    )

    

    __postprocessing_logger.info(f"Using KneeLocator, optimum is {kl.elbow}")

    kmeans_best = KMeans(n_clusters=nb_cluster_optim, **kmeans_kwargs)

    note_clusters = kmeans_best.fit_predict(X)
    
    cluster_centers = [ centroid_coordinates[0] for centroid_coordinates in kmeans_best.cluster_centers_]
    __postprocessing_logger.debug(f"Centroids : [ {cluster_centers} ]")

    return cluster_centers, note_clusters

def get_possible_bpm(fps, centroids):

    __postprocessing_logger.debug(f"Computing bpms with [ {fps} ] fps and centroids: [ {centroids} ]")

    fpm = fps* 60 # frames per minutes

    possible_bpms = [round(fpm / float(nb_frame)) for nb_frame in centroids]

    return possible_bpms

## COLOR FUNCTIONS

# Function to run K-means clustering using OpenCV's kmeans
def run_kmeans(data, num_clusters):
    # Convert data to 32-bit float
    data = np.float32(data)
    
    # Define criteria for K-means (termination criteria)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.2)
    
    # Run K-means clustering
    _, labels, centroids = cv2.kmeans(data, num_clusters, None, criteria, attempts=5, flags=cv2.KMEANS_RANDOM_CENTERS)
    
    return labels.flatten(), centroids

# Assign each point to its closest centroid (similar to the previous function)
def assign_points_to_clusters(points, centroids):
    distances = cdist(points, centroids)
    closest_centroids = np.argmin(distances, axis=1)
    return closest_centroids

# Perform K-means clustering and find the optimum number of clusters
def get_color_clusters(color_list : List[MidiScannerColor], max_clusters=4, distance_threshold=3) -> Tuple[int, List[MidiScannerColor]]:
    """Get color optimim cluter centroids

    Args:
        color_list (List[MidiScannerColor]): List of colors to perform clustering on
        max_clusters (int, optional): Max number of clusters to try. Defaults to 4.
        distance_threshold (int, optional): minimum distance between two distinct colors. Defaults to 3.

    Returns:
        Tuple[int, List[MidiScannerColor]]: (Optimal number of clusters, Clusters centroids the optimal number of clusters)
    """

    if len(color_list) == 0:
        return None, None
    
    lab_colors = [color.get_lab() for color in color_list]
    centroids_dict = {}  # To store centroids for each number of clusters
    optimum_num_clusters = None

    for num_clusters in range(1, max_clusters + 1):

        if len(color_list) < num_clusters:
            break 
        # Step 2: Apply K-means using OpenCV's K-means
        _, centroids = run_kmeans(lab_colors, num_clusters)
        
        # Store centroids
        centroids_dict[num_clusters] = [MidiScannerColor(centroid, ColorFormat.LAB) for centroid in centroids]
        
        # Step 3: Check distances between centroids if num_clusters > 1
        if num_clusters > 1:
            distances_inter_cluster = cdist(centroids, centroids)
            min_distance = np.min(distances_inter_cluster[distances_inter_cluster > 0])  # Ignore self-distances
            __postprocessing_logger.debug(f"Minimum distance between centroids for {num_clusters} clusters: {min_distance:.2f}")

            # Step 4: Determine if this is the optimum number of clusters
            if min_distance >= distance_threshold:
                optimum_num_clusters = num_clusters
            else:
                break
        else:
            optimum_num_clusters = num_clusters

    # Output results
    __postprocessing_logger.debug(f"Optimum number of clusters: {optimum_num_clusters}")

    return optimum_num_clusters, centroids_dict[optimum_num_clusters]

def get_black_white_notes(note_list : List[PlayedNote]) -> Tuple[List[PlayedNote], List[PlayedNote]]:
    
    black_list = []
    white_list = []
    for note in note_list:
        if note.is_black():
            black_list.append(note)
        else:
            white_list.append(note)
    
    return black_list, white_list


# Assume list not empty
def get_black_white_color_clusters(note_list: List[PlayedNote], max_clusters=4, distance_threshold=3) -> Tuple[int, List[MidiScannerColor], List[MidiScannerColor]]:
    """_summary_

    Args:
        note_list (List[PlayedNote]): _description_
        max_clusters (int, optional): _description_. Defaults to 4.
        distance_threshold (int, optional): _description_. Defaults to 3.

    Returns:
        Tuple[int, List[MidiScannerColor], List[MidiScannerColor]]: num_cluster, black_clusters, white_clusters
    """
    if len(note_list) == 0:
        return (None, None, None)

    black_notes, white_notes = get_black_white_notes(note_list)
    black_colors = [note.get_played_color() for note in black_notes]
    white_colors = [note.get_played_color() for note in white_notes]

    b_best_num_clusters, b_centroids = get_color_clusters(black_colors,max_clusters=max_clusters, distance_threshold=distance_threshold)
    w_best_num_clusters, w_centroids = get_color_clusters(white_colors,max_clusters=max_clusters, distance_threshold=distance_threshold)

    # At least one is not None
    overall_num_clusters = max(b_best_num_clusters, w_best_num_clusters)
    
    if b_best_num_clusters is None or w_best_num_clusters is None:
        return overall_num_clusters, b_centroids, w_centroids 

    # Both have at least one cluster - pair them together with closest matching color ()
    # Fill missing clusters

    assignements = get_color_assignment(b_centroids, w_centroids)

    if b_best_num_clusters <= w_best_num_clusters:

        # reorder white clusters
        assignements.sort(key=lambda x: x[0])
        white_assignement = [new_position[1] for new_position in assignements]
        complete_set = set(range(overall_num_clusters))
        # Find the missing integers by subtracting the given list from the complete set
        missing_clusters = complete_set - set(white_assignement)
        white_assignement = list(white_assignement) + list(missing_clusters)
        w_centroids = [w_centroids[i] for i in white_assignement]


        for _ in range(len(missing_clusters)):
            b_centroids.append(None)
    
    else:
        # reorder white clusters
        assignements.sort(key=lambda x: x[1])
        black_assignement = [new_position[0] for new_position in assignements]
        complete_set = set(range(overall_num_clusters))

        # Find the missing integers by subtracting the given list from the complete set
        missing_clusters = complete_set - set(black_assignement)
        black_assignement = black_assignement + missing_clusters
        b_centroids = b_centroids[black_assignement]

        for _ in range(len(missing_clusters)):
            w_centroids.append(None)

def get_color_assignment(color_list_1:List[MidiScannerColor], color_list_2: List[MidiScannerColor]):

    color_list_1 = [color.get_lab() for color in color_list_1]
    color_list_2 = [color.get_lab() for color in color_list_2]

    shortest_len = min(len(color_list_1), len(color_list_2))
    distances = cdist(color_list_1, color_list_2)
    distances_sorted_idx = np.argsort(distances, axis=None)

    sorted_assignments = [(e1, e2) for e1, e2 in zip((distances_sorted_idx//len(color_list_2)).tolist(), (distances_sorted_idx%len(color_list_2)).tolist())]

    assigned_elem_lists = [[],[]]

    final_assignments = []
    for assignement in sorted_assignments:
        if not any([assignement[i] in assigned_elem_lists[i] for i in range(2)]):
            final_assignments.append(assignement)
            if len(final_assignments) == shortest_len:
                return final_assignments