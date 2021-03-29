"""
    Library functions for loading the dataset
"""

# -*- coding: utf-8 -*-

import pandas as pd  
import numpy as np 
from bunch import Bunch
from tqdm import tqdm 
import time


KEY_MAP = Bunch(
    {
        "LONGITUDE" : "Longitude",
        "CATEGORY" : "Category",
        "GENDER" : "Gender",
        "START_TIME" : "Start_time",
        "END_TIME": "End_time",
        "TIME_WEIGHT" : "Time_Weight",
        "DATE" : "Date",
        "END_DATETIME": "End_Datetime",
        "WEEKDAY" : "Weekday",
        "WEEK_NUMBER" : "Week_Number",
        "MONTH_NAME" : "Month_Name",
        "MONTH_NUMBER" : "Month_Number",
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

def read_data(file_path):
    """ 
    This function loads the dataset frim the csv file into a dataframe.

    Parameters
    ----------
    file_path : str

    Returns
    -------
    df: pandas.DataFrame

    """
    ## Loading Dataset
    pbar =  tqdm (range (100), desc="Loading Data.........")
    pbar.update(50)
    time.sleep(0.3)
    df = pd.read_csv(file_path)
    pbar.update(50)
    pbar.close()
    
    ## Data Preprocessing
    df = preprocess_data(df)
    
    return df


def preprocess_data(dataset):
    """ 
    This function performs necessary preprocessing required for
    the dataset.

    Parameters
    ----------
    dataset: pandas.DataFrame

    Returns
    -------
    df: pandas.DataFrame

    """
    df = handle_series(dataset)
    pbar =  tqdm (range (100), desc="Preprocessing Data...")
    time.sleep(0.01)
    pbar.update(15)
    df[KEY_MAP.LONGITUDE] = df.Longitude.astype('float')
    df[KEY_MAP.CATEGORY] = df.Category.astype('category')
    df[KEY_MAP.GENDER] = df.Gender.astype('category')
    
    time.sleep(0.01)
    pbar.update(15)
    df[KEY_MAP.START_TIME] = pd.to_datetime(df[KEY_MAP.START_TIME])
    df[KEY_MAP.START_TIME] = pd.Series(df[KEY_MAP.START_TIME].dt.time)
    
    time.sleep(0.01)
    pbar.update(15)
    temp = pd.to_datetime(df[KEY_MAP.END_TIME])
    df[KEY_MAP.TIME_WEIGHT] = (temp.dt.hour * 60 + temp.dt.minute + temp.dt.second/60) / 1000 
    df[KEY_MAP.END_TIME] = pd.Series(temp.dt.time)
    
    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.DATE] = pd.to_datetime(df[KEY_MAP.DATE])

    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.END_DATETIME] = pd.to_datetime(df[KEY_MAP.DATE].astype(str) + ' ' + df[KEY_MAP.START_TIME].astype(str))

    time.sleep(0.01)
    pbar.update(15)
    df[KEY_MAP.WEEKDAY] = df[KEY_MAP.END_DATETIME].dt.day_name()

    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.WEEK_NUMBER] = df[KEY_MAP.END_DATETIME].dt.week
    df[KEY_MAP.WEEK_NUMBER] = df[KEY_MAP.WEEK_NUMBER] % 4

    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.MONTH_NAME] = df[KEY_MAP.END_DATETIME].dt.month_name()
    df[KEY_MAP.MONTH_NUMBER] = df[KEY_MAP.END_DATETIME].dt.month
    pbar.close()

    return df