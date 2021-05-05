#!/usr/bin/env python
# coding: utf-8

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
    # import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    import sklearn.linear_model as sk_linear
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt
    import warnings

    warnings.filterwarnings('ignore')

    df = data
    df = df.fillna(0)
    feature = ['Device_ID', 'Category_Num', 'Gender_Num', 'Geohash_Num', 'Start_time_Cat', 'End_time_Cat',
               'Start_Time_Weight', 'End_Time_Weight', 'Duration', 'Weekday', 'Week_Num',
               'Month_Num']  # ,'tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print("Train data length:", len(X_train))
    print("Test data length:", len(X_test))

    Linear_model = sk_linear.LinearRegression(fit_intercept=True, normalize=False, copy_X=True, n_jobs=1, )
    Linear_model.fit(X_train, y_train)
    acc = Linear_model.score(X_test, y_test)
    print('Linear Model:')
    # print('Intercept_:',Linear_model.intercept_)
    # print('Coef:',Linear_model.coef_)
    print('Linear Model Accuracy:', acc)

    y_pred = Linear_model.predict(X_test)

    plt.figure(facecolor='w')
    plt.plot(range(len(y_pred)), y_test, 'r-', linewidth=2, label='test')
    plt.plot(range(len(y_pred)), y_pred, 'g-', linewidth=2, label='predict')
    plt.legend(loc='upper left')
    plt.grid(True)
    # plt.show()

    print("Cross Validation:")
    scores = cross_val_score(Linear_model, X_test, y_test, cv=10).mean()
    print("Cross_Val_Score: {}".format(scores))


def Descion_Tree_model(data):
    """ 
    This function performs Descion_Tree_model on the loaded data.

    Parameters
    ----------
    data: loaded data

    Returns
    -------
    Descion_Tree_model scores

    """
    import pandas as pd
    # import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    import sklearn.linear_model as sk_linear
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt
    import warnings

    warnings.filterwarnings('ignore')

    df = data
    df = df.fillna(0)
    feature = ['Device_ID', 'Category_Num', 'Gender_Num', 'Geohash_Num', 'Start_time_Cat', 'End_time_Cat',
               'Start_Time_Weight', 'End_Time_Weight', 'Duration', 'Weekday', 'Week_Num',
               'Month_Num']  # ,'tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print("Train data length:", len(X_train))
    print("Test data length:", len(X_test))

    import sklearn.tree as sk_tree
    Descion_Tree_model = sk_tree.DecisionTreeClassifier(criterion='entropy', max_depth=None, min_samples_split=2,
                                                        min_samples_leaf=1, max_features=None, max_leaf_nodes=None,
                                                        min_impurity_decrease=0)
    Descion_Tree_model.fit(X_train, y_train)
    acc2 = Descion_Tree_model.score(X_test, y_test)

    print('Descion Tree Model:')
    print('Descion Tree Accuracy:', acc2)

    y_pred = Descion_Tree_model.predict(X_test)

    plt.figure(facecolor='w')
    plt.plot(range(len(y_pred)), y_test, 'r-', linewidth=2, label='test')
    plt.plot(range(len(y_pred)), y_pred, 'g-', linewidth=2, label='predict')
    plt.legend(loc='upper left')
    plt.grid(True)
    # plt.show()

    print("Cross Validation:")
    scores = cross_val_score(Descion_Tree_model, X_test, y_test, cv=10).mean()
    print("Cross_Val_Score: {}".format(scores))


def KNN_Class_model(data):
    """ 
    This function performs KNN_Class_model on the loaded data.
    Parameters
    ----------
    data: loaded data
    Returns
    -------
    KNN_Class_model scores
    """

    import pandas as pd
    # import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    import sklearn.linear_model as sk_linear
    from sklearn.model_selection import cross_val_score
    import matplotlib.pyplot as plt
    from sklearn import neighbors
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import GridSearchCV
    from sklearn.model_selection import train_test_split
    import warnings

    warnings.filterwarnings('ignore')

    param_grid = [{
        "weights": ["uniform"],
        "n_neighbors": [i for i in range(1, 11)]
    },
        {"weights": ["distance"],
         "n_neighbors": [i for i in range(1, 11)],
         "p": [i for i in range(1, 6)]
         }]

    knn_clf = KNeighborsClassifier()
    grid_search = GridSearchCV(knn_clf, param_grid)

    df = data
    df = df.fillna(0)
    feature = ['Device_ID', 'Category_Num', 'Gender_Num', 'Geohash_Num', 'Start_time_Cat', 'End_time_Cat',
               'Start_Time_Weight', 'End_Time_Weight', 'Duration', 'Weekday', 'Week_Num',
               'Month_Num']  # ,'tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    grid_search = GridSearchCV(knn_clf, param_grid, n_jobs=-1, verbose=2, cv=10)
    grid_search.fit(X_train, y_train)

    KNN_Class_model = neighbors.KNeighborsClassifier(n_neighbors=grid_search.best_params_['n_neighbors'],
                                                     p=grid_search.best_params_['p'],
                                                     weights=grid_search.best_params_['weights'])
    KNN_Class_model.fit(X_train, y_train)
    acc7 = KNN_Class_model.score(X_test, y_test)

    print('KNN_Class_model:')
    print('KNN_Class_model Accuracy:', acc7)

    y_pred = KNN_Class_model.predict(X_test)

    plt.figure(facecolor='w')
    plt.plot(range(len(y_pred)), y_test, 'r-', linewidth=2, label='test')
    plt.plot(range(len(y_pred)), y_pred, 'g-', linewidth=2, label='predict')
    plt.legend(loc='upper left')
    plt.grid(True)
    # plt.show()

    print("Cross Validation:")
    scores = cross_val_score(KNN_Class_model, X_test, y_test, cv=10).mean()
    print("Cross_Val_Score: {}".format(scores))

def KNN_Reg_model(data):
    """ 
    This function performs KNN_Reg_model on the loaded data.
    Parameters
    ----------
    data: loaded data
    Returns
    -------
    KNN_Reg_model scores
    """

    # import lightgbm as lgb
    from sklearn.metrics import mean_squared_error
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    import sklearn.linear_model as sk_linear
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import GridSearchCV
    from sklearn.neighbors import KNeighborsClassifier
    import matplotlib.pyplot as plt
    from sklearn import neighbors
    import warnings

    warnings.filterwarnings('ignore')

    param_grid = [{
        "weights": ["uniform"],
        "n_neighbors": [i for i in range(1, 11)]
    },
        {"weights": ["distance"],
         "n_neighbors": [i for i in range(1, 11)],
         "p": [i for i in range(1, 6)]
         }]

    knn_clf = KNeighborsClassifier()
    #grid_search = GridSearchCV(knn_clf, param_grid)

    df = data
    df = df.fillna(0)
    feature = ['Device_ID', 'Category_Num', 'Gender_Num', 'Geohash_Num', 'Start_time_Cat', 'End_time_Cat',
               'Start_Time_Weight', 'End_Time_Weight', 'Duration', 'Weekday', 'Week_Num',
               'Month_Num']  # ,'tavg','weather']
    X = df[feature]
    y = df['Next_Geohash_Num']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    print("Train data length:", len(X_train))
    print("Test data length:", len(X_test))

    grid_search = GridSearchCV(knn_clf, param_grid, n_jobs=-1, verbose=2, cv=10)
    grid_search.fit(X_train, y_train)

    KNN_Reg_model = neighbors.KNeighborsRegressor(n_neighbors=grid_search.best_params_['n_neighbors'],
                                                  p=grid_search.best_params_['p'],
                                                  weights=grid_search.best_params_['weights'])
    KNN_Reg_model.fit(X_train, y_train)
    acc8 = KNN_Reg_model.score(X_test, y_test)

    print('KNN_Reg_model:')
    print('KNN_Reg_model Accuracy:', acc8)

    y_pred = KNN_Reg_model.predict(X_test)

    plt.figure(facecolor='w')
    plt.plot(range(len(y_pred)), y_test, 'r-', linewidth=2, label='test')
    plt.plot(range(len(y_pred)), y_pred, 'g-', linewidth=2, label='predict')
    plt.legend(loc='upper left')
    plt.grid(True)
    # plt.show()

    print("Cross Validation:")
    scores = cross_val_score(KNN_Reg_model, X_test, y_test, cv=10).mean()
    print("Cross_Val_Score: {}".format(scores))