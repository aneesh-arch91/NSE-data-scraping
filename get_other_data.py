# This script is for getting other kinds of data on the NSE website
import requests as rq
import pandas as pd
import io

# A function to get all stock names from index from NSE
def get_stocks_from_index(index, headers, cookies, exclude = [], number_of_stocks=30):
    url = 'https://www.nseindia.com/api/equity-stockIndices?index=' + index + '&selectValFormat=crores'
    response = rq.get(url, headers=headers, cookies=cookies)
    equityStockJson = response.json()
    equityStockJson['data'].pop(0)
    stockData = equityStockJson['data']
    stock_list = []
    for stock in stockData:
        if (stock["meta"]["industry"] not in exclude and len(stock_list) < number_of_stocks):
            stock_list.append(stock['symbol'])
    return stock_list

