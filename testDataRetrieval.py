import unittest
import os
from data_retrieval import (
    get_all_stock_data
        )

stock = 'RELIANCE'
class DataRetreivalTest(unittest.TestCase):
    # function to test the successful data retrieval of one stock
    def testDataStock(self):
        path = 'data/' + stock + '/'
        get_all_stock_data(stock)
        filename = 'screener.html'
        self.assertIs(os.path.exists(path + filename), True)
    # function to check if the XBRL-XML files have been created
    def testXBRLfiles(self):
        path = 'data/' + stock + '/'
        for i in range(7):
            filename = 'XBRL_' + str(2018 + i) + '.xml'
            self.assertIs(os.path.exists(path + filename), True)
if __name__ == '__main__':
    unittest.main()
