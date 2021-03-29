#!/usr/bin/env python
# coding: utf-8

"""
    Library functions for EDA
"""
    
    
def EDA(data):
    
    """ 
    This function performs EDA on the loaded data.

    Parameters
    ----------
    data: loaded data

    Returns
    -------
    EDA

    """
    import seaborn as sns
    import pandas as pd
    import pandas_profiling as pp
    import matplotlib.pyplot as plt
    df = data
    report = pp.ProfileReport(df,explorative=True)
    report.to_file("DF-eda-data-profiling.html")
    print('The report has been prepared and downloaded successfully')

    import dtale
    print(dtale.show(df, ignore_duplicate=True))
