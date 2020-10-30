""" 
    Library functions for determining frequency of visits for the 
    dwell dataset.
"""

# -*- coding: utf-8 -*-

import pandas as pd  
import numpy as np 
from bunch import Bunch

KEY_MAP = Bunch(
    {
        "WEEK_NUMBER" : "Week_Number",
        "DEVICE_ID" : "Device_ID",
        "CATEGORY" : "Category",
        "MONTH_NUMBER" : "Month_Number",
        "FREQ_OF_VISITS" : "Frequency of visits",

 

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


# FIXME Dataset input should not be in Series Format
# FIXME Substitute mean with moving_average

def weekly_frequency(dataset, device_id):
    """
    The function calculates the frequency of visits on a weekly basis 
    for each category in the dataset. The frequency will be calculated
    for a specific Device_ID

    Parameters
    ----------
    dataset   : pandas.Series/pandas.Dataframe
    device_id : int

    Returns
    -------
    freq_count: pandas.Dataframe

    """
    df = handle_series(dataset)
    try:
        freq_count = df.groupby(by = [KEY_MAP.WEEK_NUMBER, KEY_MAP.DEVICE_ID, KEY_MAP.CATEGORY])[KEY_MAP.DEVICE_ID].count().unstack(KEY_MAP.DEVICE_ID).reset_index()
        freq_count = freq_count.groupby([KEY_MAP.CATEGORY]).mean()
        del freq_count[KEY_MAP.WEEK_NUMBER]
        freq_count = pd.DataFrame(freq_count[device_id].reset_index())
        freq_count.columns = [KEY_MAP.CATEGORY, KEY_MAP.FREQ_OF_VISITS]
        return freq_count
    except KeyError:
        print("Device_ID not found")


# FIXME Substitute mean with moving_average

def monthly_frequency(dataset, device_id):
    """
    The function calculates the frequency of visits on a monthly basis 
    for each category in the dataset. The frequency will be calculated
    for a specific Device_ID

    Parameters
    ----------
    dataset   : pandas.Series/pandas.Dataframe
    device_id : int

    Returns
    -------
    freq_count: pandas.Dataframe

    """
    df = handle_series(dataset)
    try:
        freq_count = df.groupby(by = [KEY_MAP.MONTH_NUMBER,KEY_MAP.DEVICE_ID,KEY_MAP.CATEGORY])[KEY_MAP.DEVICE_ID].count().unstack(KEY_MAP.DEVICE_ID).reset_index()
        freq_count = freq_count.groupby([KEY_MAP.CATEGORY]).mean()
        del freq_count[KEY_MAP.MONTH_NUMBER]
        freq_count = pd.DataFrame(freq_count[device_id].reset_index())
        freq_count.columns = [KEY_MAP.CATEGORY, KEY_MAP.FREQ_OF_VISITS]
        return freq_count
    except KeyError:
        print("Device_ID not found")