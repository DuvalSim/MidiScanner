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

def get_color_clusters(note_list : List[PlayedNote]) -> Tuple[List[MidiScannerColor],List[MidiScannerColor], List[int], List[int]] :
    """Computes the automated color clusters for white and black keys

    Args:
        note_list (List[PlayedNote]): List of black and white PlayedNotes

    Returns:
        Tuple[List[MidiScannerColor],List[MidiScannerColor], List[int], List[int]]: white/black cluster centroids, white/black cluster ids
    """
    white_keys_colors = []
    black_keys_colors = []
    for note in note_list:
        if note.is_black():
            black_keys_colors.append(note.get_played_color().get_bgr())
        else:
            white_keys_colors.append(note.get_played_color().get_bgr())
    
    if len(white_keys_colors) >= 10:
        X_white = np.array(white_keys_colors).reshape(-1,3)
        white_centroids, white_clusters_id = __get_automated_clusters(X_white)
        white_colors = [MidiScannerColor(cluster_center, ColorFormat.BGR) for cluster_center in white_centroids]

    else :
        white_colors = white_clusters_id = None

    if len(black_keys_colors) >= 10:

        X_black = np.array(black_keys_colors).reshape(-1,3)
        black_centroids, black_clusters_id = __get_automated_clusters(X_black)
        black_colors = [MidiScannerColor(cluster_center, ColorFormat.BGR) for cluster_center in black_centroids]
    else :
            black_colors = black_clusters_id = None
    return white_colors, black_colors, white_clusters_id, black_clusters_id


def __get_automated_clusters(X:ArrayLike) -> Tuple[ArrayLike, List[int]]: 
    
    if len(X.shape) != 2:
        __postprocessing_logger.critical(f"Array must be of size 2 - shape is: [{X.shape}]")


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

    # plt.plot(range(1,9), sse)
    # plt.show()

    # we assume inertia is going down 
    
    # baseline = sse[0]
    # previous = sse[0]
    # nb_cluster_optim = 0
    # for i, inertia in enumerate(sse[1:]):
    #     drop = (previous - inertia ) / baseline
    #     __postprocessing_logger.debug(f"Drop: [{drop}]")
    #     if drop < 0.01:
    #         nb_cluster_optim = i + 1
    #         break
    #     previous = inertia
    # else:
    #     nb_cluster_optim = len(sse)
    #     __postprocessing_logger.warning("Did not find optimum number of clusters")

    # __postprocessing_logger.debug(f"Inertias : [{sse}]")
    # __postprocessing_logger.info(f"Using [{nb_cluster_optim}] clusters")

    kl = KneeLocator(
        range(1,9), sse, curve="convex", direction="decreasing"
    )

    __postprocessing_logger.info(f"Using KneeLocator, optimum is {kl.elbow}")

    kmeans_best = KMeans(n_clusters=kl.elbow, **kmeans_kwargs)

    cluster_idx = kmeans_best.fit_predict(X)
    
    cluster_centers = kmeans_best.cluster_centers_

    return cluster_centers, cluster_idx.tolist()
