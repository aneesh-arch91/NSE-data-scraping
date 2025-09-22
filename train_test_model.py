# This script is for training and testing a model
# Firstly, I will train a simple model which will train on 18 stocks data and test on 2 stocks.
import numpy as np
from organize_data import OrganizeData
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.svm import NuSVC
import seaborn as sns
import matplotlib.pyplot as plt

# function to modify the financial dataframe to make it more suitable for training
def modify_financial_df(stock, df):
    if df.empty:
        return df
    old_index_list = df.index.values.tolist()
    for index in old_index_list:
        df.rename(index={index: (stock, index)}, inplace=True)
    return df

# function to combine the 20 stocks dataframe.
def get_stock_combined_df(stocklist, headers={}, cookies={}):
    stock = stocklist[0]
    stock_data_obj = OrganizeData(stock, headers, cookies)
    print(stock)
    financials_df = stock_data_obj.get_financials_halecs()
    combined_df = modify_financial_df(stock, financials_df)
    for i in range(1, len(stocklist)):
        stock = stocklist[i]
        print(stock) 
        stock_data_obj = OrganizeData(stock, headers, cookies)
        financials_df = stock_data_obj.get_financials_halecs()
        modified_df = modify_financial_df(stock, financials_df)
        combined_df = pd.concat([combined_df, modified_df], axis=0)
        df_columns = combined_df.columns.tolist()
    return combined_df

def split_data_random(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=50) 
    return X_train, X_test, y_train, y_test
def split_data_stock(X, y):
    X_train = X[:-14]
    y_train = y[:-14]
    X_test = X[-14:]
    y_test = y[-14:]
    return X_train, X_test, y_train, y_test

def get_trained_model(X_train, y_train, model_function, weights=None):
    if weights is None:
        return model_function().fit(X_train, y_train)
    else:
        return model_function(weights=weights).fit(X_train, y_train)

def get_r2_score(trained_model, X_test, y_test):
    y_pred = trained_model.predict(X_test)
    return r2_score(y_pred, y_test)

def get_accuracy(trained_model, X_test, y_test):
    y_pred = trained_model.predict(X_test)
    return accuracy_score(y_pred, y_test)

def get_cross_val_results(model, X, y, cv=5):
    result = cross_val_score(model, X, y, cv=cv)
    print(result)
    return np.mean(result)

def main():
    stocks_data_df = pd.read_csv('combined_data.csv', index_col=0)
    # some EDA first
    #print(stocks_data_df.head())
    #filtered_df = stocks_data_df[stocks_data_df.nunique(axis=1) == 5]
    X = stocks_data_df.drop(['Returns'], axis=1)
    filtered_df = X[(X.eq(1.0).sum(axis=1)) == 5]
    print(filtered_df)
    #X = stocks_data_df[['D/E ratio', 'P.E ratio']]
    #y = stocks_data_df[['Returns']].values.ravel()
    #X_train, X_test, y_train, y_test = split_data_random(X, y) 
    #model = get_trained_model(X_train, y_train, KNeighborsClassifier, weights='distance')
    #print(get_accuracy(model, X_test, y_test)) 
    #print(stocks_data_df[['Absolute Return Next Year']].describe())
    #print(y)
    #print(get_cross_val_results(LogisticRegression(class_weight='balanced'), X, y, cv=5))
    #print(get_cross_val_results(NuSVC(class_weight = 'balanced'), X, y, cv=5))
    #print(get_cross_val_results(KNeighborsClassifier(weights = 'distance'), X, y, cv=5))
    #for i in range(len(stocks_data_df.columns[:-1])):
    #    label = stocks_data_df.columns[i]
    #    plt.hist(stocks_data_df[stocks_data_df['Returns'] == 1][label], color='green', label="More than 20% Positive Return", alpha=0.7)
    #    plt.hist(stocks_data_df[stocks_data_df['Returns'] == 0][label], color='red', label="Less than 20% Positive Return", alpha=0.7)
    #    plt.title(label)
    #    plt.ylabel("N")
    #    plt.xlabel(label)
    #    plt.legend()
    #    plt.show()
    #sns.heatmap(stocks_data_df.corr(), cmap='vlag', annot=True, fmt=".2f")
    #sns.heatmap(stocks_data_df.corr(), cmap="vlag", annot=True, fmt=".2f")
    #plt.show()

if __name__ == '__main__':
    main()
