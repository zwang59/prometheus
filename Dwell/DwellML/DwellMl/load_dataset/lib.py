#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
    Library functions for loading the dataset
"""

import pandas as pd  
import numpy as np 
from bunch import Bunch
from tqdm import tqdm 
import time
import geohash as gh
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Stations, Daily
import warnings

warnings.filterwarnings('ignore')


KEY_MAP = Bunch(
    {
        "LONGITUDE" : "Longitude",
        "CATEGORY" : "Category",
        "GENDER" : "Gender",
        "START_TIME" : "Start_time",
        #"START_TIME_CAT" : "Start_time_Cat",
        "END_TIME": "End_time",
        #"END_TIME_CAT": "End_time_Cat",
        "START_TIME_WEIGHT" : "Start_Time_Weight",
        "END_TIME_WEIGHT" : "End_Time_Weight",
        "DATE" : "Date",
        "END_DATETIME": "End_Datetime",
        "WEEKDAY" : "Weekday",
        "WEEK_NUMBER" : "Week_Num",
        "MONTH_NAME" : "Month_Name",
        "MONTH_NUMBER" : "Month_Num",
        "GEO_HASH" : "Geohash",
        "DURATION" : "Duration",
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
    pbar =  tqdm (range (100), desc="Loading Data......")
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
    pbar =  tqdm (range (100), desc="Preprocessing Data")
    time.sleep(0.01)
    pbar.update(15)
    df[KEY_MAP.LONGITUDE] = df.Longitude.astype('float')
    df[KEY_MAP.CATEGORY] = df.Category.astype('category')
    df[KEY_MAP.GENDER] = df.Gender.astype('category')
    
    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.GEO_HASH] = df.apply(lambda x: gh.encode(x.Latitude, x.Longitude), axis =1)
    df[KEY_MAP.GEO_HASH] = df.Geohash.astype('category')
    
    time.sleep(0.01)
    pbar.update(10)
    CAT_COLUMNS_NUM = []
    cat_columns = df.select_dtypes(['category']).columns
    for column in cat_columns:
        df[column + "_Num"] = df[column]
        CAT_COLUMNS_NUM.append(column + "_Num")
    df[CAT_COLUMNS_NUM] = df[cat_columns].apply(lambda x: x.cat.codes+1)
    
    time.sleep(0.01)
    pbar.update(10)
    csv_df = df
    csv_df['Start_Datetime'] = csv_df['Date'] + " " + csv_df['Start_time']
    csv_df['Start_Datetime'] = pd.to_datetime(csv_df['Start_Datetime'])
    csv_df['End_Datetime'] = csv_df['Date'] + " " + csv_df['End_time']
    csv_df['End_Datetime'] = pd.to_datetime(csv_df['End_Datetime'])
    
    csv_df['Start_time_Cat'] = np.nan
    csv_df['Start_time_Cat'].loc[(csv_df['Start_Datetime'].dt.hour < 12) & (csv_df['Start_Datetime'].dt.hour >= 4)] = 1 #morning
    csv_df['Start_time_Cat'].loc[(csv_df['Start_Datetime'].dt.hour < 17) & (csv_df['Start_Datetime'].dt.hour >= 12) ] = 2 #noon
    csv_df['Start_time_Cat'].loc[(csv_df['Start_Datetime'].dt.hour < 20) & (csv_df['Start_Datetime'].dt.hour >= 17)] = 3 #evening
    csv_df['Start_time_Cat'].loc[(csv_df['Start_Datetime'].dt.hour < 4) | (csv_df['Start_Datetime'].dt.hour >= 20)] = 4 #night

    csv_df['End_time_Cat'] = np.nan
    csv_df['End_time_Cat'].loc[(csv_df['End_Datetime'].dt.hour < 12) & (csv_df['End_Datetime'].dt.hour >= 4)] = 1 #morning
    csv_df['End_time_Cat'].loc[(csv_df['End_Datetime'].dt.hour < 17) & (csv_df['End_Datetime'].dt.hour >= 12) ] = 2 #noon
    csv_df['End_time_Cat'].loc[(csv_df['End_Datetime'].dt.hour < 20) & (csv_df['End_Datetime'].dt.hour >= 17)] = 3 #evening
    csv_df['End_time_Cat'].loc[(csv_df['End_Datetime'].dt.hour < 4) | (csv_df['End_Datetime'].dt.hour >= 20)] = 4 #night
    
    
    csv_df = csv_df.sort_values(by=['Device_ID','Start_Datetime'], ascending=[True, True])
    Device_Id_Num_info = csv_df['Device_ID'].unique()
    csv_df_2 = pd.DataFrame()
    for tem_Device_Id_Num_info in Device_Id_Num_info:
        temp_data = csv_df[csv_df['Device_ID'].isin([tem_Device_Id_Num_info])]
        temp_data = temp_data.reset_index(drop=True)
        temp_data['Next_Geohash_Num'] = np.nan
        for i in range(0,len(temp_data['Geohash_Num'])):
            if i == (len(temp_data['Geohash_Num'])-1):
                temp_data['Next_Geohash_Num'][i] = temp_data['Geohash_Num'][i]
            else:
                temp_data['Next_Geohash_Num'][i] = temp_data['Geohash_Num'][i+1]
        csv_df_2 = pd.concat([temp_data,csv_df_2])
    df = csv_df_2.reset_index(drop=True)
    
    time.sleep(0.01)
    pbar.update(15)
    df['Datetime'] = pd.to_datetime(df['Date'])
    df['year'] = df['Datetime'].dt.year
    df['month'] = df['Datetime'].dt.month
    df['day'] = df['Datetime'].dt.day
    df[["tavg","tmin", "tmax", "prcp", "snow","wdir","wspd"]] = np.nan
    #df[["tmin", "tmax", "prcp", "snow"]] = np.nan
    for i in range(0,len(df['Datetime'])):
        # Get weather stations ordered by distance to Vancouver, BC
        stations = Stations(lat = df['Latitude'][i], lon = df['Longitude'][i], daily = datetime(df['year'][i], df['month'][i], df['day'][i]))
        # Fetch closest station (limit = 1)
        station = stations.fetch(1)
        # Get daily data for date at the selected weather station
        data = Daily(station, start = datetime(df['year'][i], df['month'][i], df['day'][i]), end = datetime(df['year'][i], df['month'][i], df['day'][i]))
        # Fetch Pandas DataFrame
        data = data.fetch()
        #prcp precipitation, wdir wind direction, wspd wind speed
        try:
            df["tavg"][i]=data["tavg"][0]
            df["tmin"][i]=data["tmin"][0]
            df["tmax"][i]=data["tmax"][0]
            df["prcp"][i]=data["prcp"][0]
            df["snow"][i]=data["snow"][0]
            df["wdir"][i]=data["wdir"][0]
            df["wspd"][i]=data["wspd"][0]
        except Exception as e:
            pass
        continue
    del df['Datetime']
    del df['year']
    del df['month']
    del df['day']
    
    df = df.fillna(0)
    df['weather'] = np.nan
    df['tavg'] = (df['tmin']+df['tmax'])/2
    df['weather'].loc[(df['prcp'] == 0) & (df['snow'] == 0) & (df['wspd'] == 0)] = 1 #sunny
    df['weather'].loc[(df['prcp'] > 0) & (df['snow'] == 0)] = 2 #rainy
    df['weather'].loc[(df['prcp'] == 0) & (df['snow'] > 0)] = 3 #snow
    df['weather'].loc[(df['prcp'] > 0) & (df['snow'] > 0)] = 4 #rainy+snow
    df['weather'].loc[(df['prcp'] == 0) & (df['snow'] == 0) & (df['wspd'] > 0)] = 5 #windy
    
    
    time.sleep(0.01)
    pbar.update(15)
    df[KEY_MAP.START_TIME] = pd.to_datetime(df[KEY_MAP.START_TIME])
    df[KEY_MAP.START_TIME] = pd.Series(df[KEY_MAP.START_TIME].dt.time)
    

    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.START_TIME] = df[KEY_MAP.START_TIME].astype(str)
    temp = pd.to_datetime(df[KEY_MAP.START_TIME])
    df[KEY_MAP.START_TIME_WEIGHT] = (temp.dt.hour * 60 + temp.dt.minute + temp.dt.second/60) 
    df[KEY_MAP.START_TIME] = pd.Series(temp.dt.time)

    temp = pd.to_datetime(df[KEY_MAP.END_TIME])
    df[KEY_MAP.END_TIME_WEIGHT] = (temp.dt.hour * 60 + temp.dt.minute + temp.dt.second/60) 
    df[KEY_MAP.END_TIME] = pd.Series(temp.dt.time)
    df[KEY_MAP.DURATION] = abs( df[KEY_MAP.START_TIME_WEIGHT] - df[KEY_MAP.END_TIME_WEIGHT])

    
    
    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.DATE] = pd.to_datetime(df[KEY_MAP.DATE])

    # df[KEY_MAP.END_DATETIME] = pd.to_datetime(df[KEY_MAP.DATE].astype(str) + ' ' + df[KEY_MAP.START_TIME].astype(str))

    time.sleep(0.01)
    pbar.update(10)
    #df[KEY_MAP.WEEKDAY] = df[KEY_MAP.DATE].dt.day_name()
    df[KEY_MAP.WEEKDAY] = df[KEY_MAP.DATE].dt.weekday + 1
    
    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.WEEK_NUMBER] = df[KEY_MAP.DATE].dt.week
    df[KEY_MAP.WEEK_NUMBER] = df[KEY_MAP.WEEK_NUMBER] % 4

    time.sleep(0.01)
    pbar.update(10)
    df[KEY_MAP.MONTH_NAME] = df[KEY_MAP.DATE].dt.month_name()
    df[KEY_MAP.MONTH_NUMBER] = df[KEY_MAP.DATE].dt.month
    
    
    pbar.close()
    
    return df

