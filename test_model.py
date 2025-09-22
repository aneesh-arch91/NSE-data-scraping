import unittest
import browser_cookie3
from organize_data import OrganizeData
from train_test_model import (
        modify_financial_df,
        get_stock_combined_df
        )
cookies = browser_cookie3.chromium()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}

#stock = 'RELIANCE'
#stock_data_obj = OrganizeData(stock, headers, cookies)
#financials_df = stock_data_obj.get_financials_df()
#stocklist = ['JBMA', 'HINDCOPPER', 'GMDCLTD', 'GRSE', 'BEML', 'GPPL', 'COCHINSHIP', 'BDL', 'DATAPATTNS', 'MAZDOCK', 'NUVAMA', 'HFCL', 'SUPREMEIND', 'MOTHERSON', 'TRITURBINE', 'IDEA', 'ADANIPOWER', 'BEL', 'HAL', 'HINDZINC']
#stocklist = ['JBMA', 'HINDCOPPER', 'GMDCLTD', 'GRSE', 'BEML', 'GPPL', 'COCHINSHIP', 'BDL', 'DATAPATTNS', 'MAZDOCK', 'NUVAMA', 'HFCL', 'SUPREMEIND', 'MOTHERSON', 'TRITURBINE', 'IDEA', 'ADANIPOWER', 'BEL', 'HAL', 'HINDZINC', 'OLECTRA', 'SOLARINDS', 'VEDL', 'TITAGARH', 'RAILTEL', 'GLAND', 'JINDALSAW', 'LUPIN', 'NEULANDLAB', 'FLUOROCHEM', 'INDUSTOWER', 'HBLENGINE', 'PNBHOUSING', 'POWERINDIA', 'NLCINDIA']
#stocklist = ['REDINGTON', 'GODFRYPHLP', 'AEGISLOG', 'KIRLOSENG', 'AADHARHFC', 'KIRLOSBROS', 'SUNDRMFAST', 'TEJASNET', 'GMRAIRPORT', 'MGL', 'TARIL', 'TTML', 'NEULANDLAB', 'RPOWER', 'GESHIP', 'CEATLTD', 'KPRMILL', 'ELECON', 'WELSPUNLIV', 'MASTEK', 'TATACOMM', 'CHOLAHLDNG', 'JKCEMENT', 'GSPL', 'CANFINHOME', 'CYIENT', 'BHARTIHEXA', 'MEDANTA', 'BAJAJHFL', 'BAYERCROP', 'SWIGGY', 'GUJGASLTD', 'AMBER', 'PVRINOX', 'TRIDENT', 'VTL', 'BLUESTARCO', 'RAYMONDLSL', 'PREMIERENE', 'MRF', 'PAGEIND', 'WOCKPHARMA', 'BALKRISIND', 'MOTHERSON', 'JSWINFRA', 'WESTLIFE', 'NTPCGREEN', 'USHAMART', 'WHIRLPOOL', 'TATAPOWER', 'ABREL', 'NHPC', 'UBL', 'NCC', 'NAVA', 'SYRMA', 'JKTYRE', 'HINDCOPPER', 'SUZLON', 'JSWENERGY', 'DEEPAKNTR', 'APOLLOTYRE', 'CAMPUS', 'LT', 'BHARATFORG', 'SCHNEIDER', 'VEDL', 'CONCOR', 'SUPREMEIND', 'RAYMOND', 'SCHAEFFLER', 'GRAPHITE', 'BHARTIARTL', 'UNOMINDA', 'CHAMBLFERT', 'POLICYBZR', 'OFSS', 'COROMANDEL', 'NAVINFLUOR', 'DATAPATTNS', 'GLAND', 'BOSCHLTD', 'NETWORK18', 'NBCC', 'NTPC', 'HYUNDAI', 'MINDACORP', 'METROPOLIS', 'AKUMS', 'JSWSTEEL', 'ZENSARTECH', 'CRAFTSMAN', '360ONE', 'POLYCAB', 'BASF', 'BERGEPAINT', 'ROUTE', 'EIDPARRY', 'SHREECEM']
combined_stock_df = get_stock_combined_df(stocklist, headers, cookies)

class TestModel(unittest.TestCase):
    # test if the dataframe has been successfully modified
    #def testModifiedDataframe(self):
    #    modified_df = modify_financial_df(stock, financials_df)
    #    print(modified_df)
    def testCombinedDataFrame(self):
        print(combined_stock_df)
        combined_stock_df.to_csv('combined_data.csv')

if __name__ == '__main__':
    unittest.main()
