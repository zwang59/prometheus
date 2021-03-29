""" 
    Library functions for calculating mode of transport
"""

# -*- coding: utf-8 -*-

import pandas as pd  
import numpy as np 
import googlemaps

MODE = ["WALK", "CAR", "BICYCLE", "TRANSIT"]
API_key = 'AIzaSyCPrYWI_KdXd8fc32Lm6M6oydwpcE7ATQ8'
gmaps = googlemaps.Client(key=API_key)

def get_vehicle(Lat1,Lat2,Lon1,Lon2,stay_duration):
    """
    If the input is of type pandas.Series, it converts to pandas.Dataframe

    Parameters
    ----------
    Lat1 : float
    Lon1 : float
    Lat2 : float
    Lon2 : float
    stay_duration : int (in seconds)


    Returns
    -------
    MODE : str

    """
    origin = (Lat1,Lon1)
    destination = (Lat2,Lon2)
    result = []

    ## Walk
    if gmaps.distance_matrix(origin, destination, mode='walking')["rows"][0]["elements"][0]["status"] == 'OK':
        walking = gmaps.distance_matrix(origin, destination, mode='walking')["rows"][0]["elements"][0]["duration"]["value"]
    else:
        walking = -1
    result.append(walking)

    ## Car
    if gmaps.distance_matrix(origin, destination, mode='driving')["rows"][0]["elements"][0]["status"] == 'OK':
        driving = gmaps.distance_matrix(origin, destination, mode='driving')["rows"][0]["elements"][0]["duration"]["value"]
    else:
        driving = -1
    result.append(driving)

    ## Bicycle
    if gmaps.distance_matrix(origin, destination, mode='bicycling')["rows"][0]["elements"][0]["status"] == 'OK':
        bicycling = gmaps.distance_matrix(origin, destination, mode='bicycling')["rows"][0]["elements"][0]["duration"]["value"]
    else:
        bicycling = -1
    result.append(bicycling)

    ## Public Transport
    if gmaps.distance_matrix(origin, destination, mode='transit')["rows"][0]["elements"][0]["status"] == 'OK':
        transit = gmaps.distance_matrix(origin, destination, mode='transit')["rows"][0]["elements"][0]["duration"]["value"]
    else:
        transit = -1
    result.append(transit)

    ## Finding the best Mode of Transport
    result = np.asarray(result) 
    index = (np.abs(result - stay_duration)).argmin()
    
    return MODE[index]