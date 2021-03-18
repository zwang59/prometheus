#!/usr/bin/env python
# coding: utf-8

"""
    Library functions for ANN models
"""
def ANN_model(data):
    """ 
    This function performs ANN_model on the loaded data.

    Parameters
    ----------
    data: loaded data

    Returns
    -------
    ANN_model scores

    """
    import pandas as pd
    from sklearn import metrics
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import GridSearchCV
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt
    
    import warnings

    warnings.filterwarnings('ignore')
    
    df = data
    feature = ['Device_ID','Category_Num','Gender_Num','Geohash_Num','Start_time_Cat','End_time_Cat','Start_Time_Weight','End_Time_Weight','Duration','Weekday','Week_Num','Month_Num','tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    scaler = MinMaxScaler()
    scaler.fit(X_train)

    scaled_train_data = scaler.transform(X_train)
    scaler_test_data = scaler.transform(X_test)



    param_grid = {

        'hidden_layer_sizes': [(10, ), (15, ), (20, ), (5, 5)],

        'activation': ['logistic', 'tanh', 'relu'],

        'alpha': [0.001, 0.01, 0.1, 0.2, 0.4, 1, 10]
    }

    mlp = MLPClassifier(max_iter=1000)

    gcv = GridSearchCV(estimator=mlp, param_grid=param_grid, cv=4, n_jobs=-1)
    gcv.fit(scaled_train_data, y_train)
    
    
    mlp = MLPClassifier(hidden_layer_sizes=gcv.best_params_['hidden_layer_sizes'], activation=gcv.best_params_['activation'], alpha=gcv.best_params_['alpha'], max_iter=1000)

    mlp.fit(scaled_train_data, y_train)

    print(mlp)
    
    train_predict = mlp.predict(scaled_train_data)
    test_predict = mlp.predict(scaler_test_data)


    train_proba = mlp.predict_proba(scaled_train_data)
    test_proba = mlp.predict_proba(scaler_test_data)    


    print(metrics.confusion_matrix(y_test, test_predict))
    print(metrics.classification_report(y_test, test_predict))  

    print(mlp.score(scaler_test_data, y_test))
    
    plt.figure(facecolor='w')  
    plt.plot(range(len(test_predict)),y_test,'r-',linewidth=2,label='test')
    plt.plot(range(len(test_predict)),test_predict,'g-',linewidth=2,label='predict')
    plt.legend(loc='upper left') 
    plt.grid(True)  
    plt.show()


    

