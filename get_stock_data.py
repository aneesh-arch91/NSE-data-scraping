# Loading the necessary libraries and initial setup 
import requests as rq
import browser_cookie3
from datetime import datetime, timedelta
import pandas as pd
import os
import io
from bs4 import BeautifulSoup
import sys
cookies = browser_cookie3.librewolf()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}
class StockPriceData:
    years = [2018 + x for x in range(6)]
    def __init__(self, stock, headers, cookies):
        self.stock = stock
        self.headers = headers
        self.cookies = cookies
        self.path = 'data/' + stock + '/'
        self.data_retrieval_status = True

    # A function that downloads the csv files containing stock prices for a date
    def get_stock_prices_csv(self, date):
        url = "https://www.nseindia.com/api/historical/cm/equity?symbol=" + self.stock + "&series=[%22EQ%22]&from=" + date + "&to=" + date + "&csv=true"
        response = rq.get(url, headers=self.headers, cookies=self.cookies)
        csv = response.content
        price_df = pd.read_csv(io.StringIO(csv.decode("utf-8")))
        # if the stock prices for this day are not available then look for the other day
        init_date_obj = datetime.strptime(date, '%d-%m-%Y')
        previous_day = init_date_obj - timedelta(days=1)
        while (price_df.empty and (init_date_obj - previous_day).days <= 30):
            print("resource not found")
            date_obj = datetime.strptime(date, '%d-%m-%Y')
            previous_day = date_obj - timedelta(days=1)
            date = previous_day.strftime('%d-%m-%Y')
            url = "https://www.nseindia.com/api/historical/cm/equity?symbol="+ self.stock + "&series=[%22EQ%22]&from=" + date + "&to=" + date + "&csv=true"
            response = rq.get(url, headers=self.headers, cookies=self.cookies)
            csv = response.content
            price_df = pd.read_csv(io.StringIO(csv.decode("utf-8")))
        if (price_df.empty):
            print("Data incomplete! Aborting...")
            self.data_retrieval_status = False
            with open(self.path + 'statusfile' , 'w') as f:
                f.write("Incomplete")
            return 
        return csv

    # function to write the csv to a file
    def write_stock_prices(self, date, csv, filename=''):
        if (filename == ''):
            filename = "price_" + date + ".csv"
        with open(self.path + filename, 'wb') as f:
            f.write(csv)
            print("stock price data written ", filename)

    # Now, let's write a function that downloads the stock prices corresponding to every year
    def get_stockprice_csv_previous_years(self):
        for year in StockPriceData.years:
            date1 = "01-04" + "-" + str(year + 1)
            date2 = "01-04" + "-" + str(year + 2)
            filename1 = "price_" + str(year) + "_1_" + ".csv"
            filename2 = "price_" + str(year) + "_2_" + ".csv"
            if (not os.path.isfile(self.path + filename1)):
                csv = self.get_stock_prices_csv(date1)
                if csv is None:
                    return
                self.write_stock_prices(date1, csv, filename1)
            if (not os.path.isfile(self.path + filename2)):
                csv = self.get_stock_prices_csv(date2)
                if csv is None:
                    return
                self.write_stock_prices(date2, csv, filename2)

    # The process for the last year will be a bit different as the next year is not complete yet.
    def get_last_years_stockprice(self):
        last_year = StockPriceData.years[-1] + 1
        date1 = "01-04" + "-" + str(last_year + 1)
        # get today's date
        date_today = datetime.today()
        date_yesterday = (date_today - timedelta(days=1)).strftime('%d-%m-%Y')
        # for the last year
        filename1 = "price_" + str(last_year) + "_1_" + ".csv"
        filename2 = "price_" + str(last_year) + "_2_" + ".csv"
        if (not os.path.isfile(self.path + filename1)):
            csv = self.get_stock_prices_csv(date1)
            self.write_stock_prices(date1, csv, filename1)
        if (not os.path.isfile(self.path + filename2)):
            csv = self.get_stock_prices_csv(date_yesterday)
            self.write_stock_prices(date_yesterday, csv, filename2)

    def get_all_stock_data(self):
        self.get_stockprice_csv_previous_years()
        if (self.data_retrieval_status):
            self.get_last_years_stockprice()
