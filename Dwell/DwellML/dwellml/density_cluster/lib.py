"""
    Library functions for clustering the dwell dataset.
"""

# -*- coding: utf-8 -*-

import pandas as pd  
import numpy as np 
from bunch import Bunch
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint

KEY_MAP = Bunch(
    {
        "LATITUDE" : "Latitude",
        "LONGITUDE" : "Longitude",
    }
)

def handle_series(dataset):
    """
    If the input is of type pandas.Series, it converts to pandas.Dataframe

    Parameters
    ----------
    dataset: pandas.Series/pandas.Dataframe

    Returns
    -------
    dataset: pandas.Dataframe

    """
    if isinstance(dataset, pd.Series):
        return pd.DataFrame(dataset)
    else:
        return dataset

def get_hot_spots(max_distance,min_devices,dataset):
    """
    This Function runs a DBSCAN algorithm on the dataset to create 
    clusters of device_id based on Frequency of visits (Density based
    clustering approach)

    Parameters
    ----------
    max_distance : float
    min_devices  : float
    dataset      : pandas.DataFrame

    Returns
    -------
    hot_spots : list
    df        : pandas.Dataframe

    """
    df = handle_series(dataset)
    df_data = df[[KEY_MAP.LATITUDE, KEY_MAP.LONGITUDE]]
    ## get coordinates from dataset
    coords = df_data.to_numpy()

    ## calculate epsilon parameter using distance
    kms_per_radian = 6371.0088
    epsilon = max_distance / kms_per_radian
    
    db = DBSCAN(eps=epsilon, min_samples=min_devices,
                algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    
    ## grouping the clusters
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

    df = df.assign(cluster=pd.Series(db.labels_))
    df = pd.DataFrame(df)

    print('Number of clusters: {}'.format(num_clusters))
    
    ## returning hot spots
    lat = []
    lon = []
    num_members = []
    
    # loop through clusters and get centroids, number of members
    for i in range(len(clusters)):

        ## filter empty clusters
        if clusters[i].any():

            ## get centroid and magnitude of cluster
            lat.append(MultiPoint(clusters[i]).centroid.x)
            lon.append(MultiPoint(clusters[i]).centroid.y)
            num_members.append(len(clusters[i]))
            
    hot_spots = [lon,lat,num_members]
    
    return hot_spots, df