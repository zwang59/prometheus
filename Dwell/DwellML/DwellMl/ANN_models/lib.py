#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
    Library functions for ML models
"""
def Linear_model(data):
    
    """ 
    This function performs linear regression on the loaded data.

    Parameters
    ----------
    data: loaded data

    Returns
    -------
    linear regression scores

    """
    import pandas as pd
    import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    import sklearn.linear_model as sk_linear
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt

    df = pd.read_csv(data)
    df = df.fillna(0)
    feature = ['Device_ID','Category_Num','Gender_Num','Geohash_Num','Start_time_Cat','End_time_Cat','Start_Time_Weight','End_Time_Weight','Duration','Weekday','Week_Num','Month_Num','tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print("Train data length:", len(X_train))
    print("Test data length:", len(X_test))
    
    Linear_model = sk_linear.LinearRegression(fit_intercept=True,normalize=False,copy_X=True,n_jobs=1,)
    Linear_model.fit(X_train,y_train)
    acc=Linear_model.score(X_test,y_test) 
    print('Linear Model:')
    #print('Intercept_:',Linear_model.intercept_)
    #print('Coef:',Linear_model.coef_) 
    print('Linear Model Accuracy:',acc)
    
    y_pred = Linear_model.predict(X_test)
    
    plt.figure(facecolor='w')  
    plt.plot(range(len(y_pred)),y_test,'r-',linewidth=2,label='test')
    plt.plot(range(len(y_pred)),y_pred,'g-',linewidth=2,label='predict')
    plt.legend(loc='upper left') 
    plt.grid(True)  
    plt.show()
  
    print("Cross Validation:")
    scores  = cross_val_score(Linear_model, X_test, y_test, cv=10).mean()
    print("Cross_Val_Score: {}".format(scores))
    
    

