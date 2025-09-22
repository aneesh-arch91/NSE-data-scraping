import unittest
import os
import xml.etree.ElementTree as ET
import browser_cookie3

from organize_data import OrganizeData
cookies = browser_cookie3.chromium()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}

stock = 'CGPOWER'
#shareholder_equity = 194236800000
stock_data_obj = OrganizeData(stock, headers, cookies)
#financials_df = stock_data_obj.get_financials_df()

class TestOrganizingData(unittest.TestCase):
    # test if the function was able to get the shareholder equity from a xml tree
    #def testShareholderEquity(self):
    #    se_list = stock_data_obj.get_shareholders_equity()
    #    self.assertEqual(se_list[-2], shareholder_equity)
    # test if promoters share works
    def testPromotersShare(self):
        promoters_pledge = stock_data_obj.get_promoters_pledge()
        #print(promoters_pledge)
        self.assertEqual(len(promoters_pledge), 7)
    # test new d/e ratio category
    def testDERatio(self):
        new_de_list = stock_data_obj.get_de_ratio_category()
        #print(new_de_list)
        self.assertEqual(len(new_de_list), 4)
    # test the new p.e ratio category
    def testPERatio(self):
        new_pe_list = stock_data_obj.get_pe_ratio_category()
        #print(new_pe_list)
        self.assertEqual(len(new_pe_list), 4)
    # test the new financial dataframe
    def testFinancialDFNew(self):
        financial_df = stock_data_obj.get_financials_halecs()
        print(financial_df)
        self.assertEqual(financial_df.shape[0], 4)

    # test if a valid dataframe is returned
    #def test_financials_dataframe(self):
    #    # simply print the dataframe
    #    print(financials_df)
    #    self.assertEqual(True, True)
if __name__ == '__main__':
    unittest.main()
