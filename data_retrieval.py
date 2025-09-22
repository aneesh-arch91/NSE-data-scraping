# Initial Setup
import os
import browser_cookie3
from get_xbrl_data import XBRLRetrieval
from get_stock_data import StockPriceData
cookies = browser_cookie3.chromium()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}
#from get_other_data import get_promoters_share

# This script is for retrieving data for one stock and putting in the appropriate folder.
def get_all_stock_data(stock):
    path = 'data/' + stock + '/'
    statusfile = 'statusfile'
    if (not os.path.exists(path)):
        os.makedirs(path)
    stock_data_obj = XBRLRetrieval(stock, headers, cookies)
    stock_data_obj.get_all_xbrl_files()
    if (not stock_data_obj.get_retrieval_status()):
        print("Data incomplete, aborting...")
        with open(path + statusfile, 'w') as f:
            f.write("Incomplete")
        return
    else:
        with open(path + statusfile, 'w') as f:
            f.write("Success")
    stock_price_obj = StockPriceData(stock, headers, cookies)
    #stock_price_obj.get_stockprice_csv_previous_years()
    #stock_price_obj.get_last_years_stockprice()
    stock_price_obj.get_all_stock_data()


if __name__ == '__main__':
    stock = 'ARCHIES'
    get_all_stock_data(stock)
