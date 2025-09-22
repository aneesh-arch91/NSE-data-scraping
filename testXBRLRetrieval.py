import unittest
import browser_cookie3
import os
import pandas as pd
from bs4 import BeautifulSoup
import get_xbrl_data
cookies = browser_cookie3.librewolf()
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}

stock = 'RELIANCE'
stock_data_obj = get_xbrl_data.XBRLRetrieval(stock, headers, cookies)
#raw_xml = stock_data_obj.get_latest_financials_XML()
#stock_data_obj.get_all_link_files()
#stock_data_obj.download_xbrl_files()
class DataRetrievalTest(unittest.TestCase):
    # test if the function return is a valid XML
    #def test_is_xml_valid(self):
    #    xml_check_str1 = '<?xml version="1.0" encoding="UTF-8"'
    #    self.assertIn(xml_check_str1, raw_xml)
    ## test if xml has the relevant data, only to check if it has total equity
    #def test_is_latest_data_adequate(self):
    #    check_data_str = '<in-capmkt:Equity '
    #    self.assertIn(check_data_str, raw_xml)
    ## test if the links files are downloaded
    #def testLinksFiles(self):
    #    path = 'data/' + stock + '/' + 'links4.html'
    #    self.assertIs(os.path.exists(path), True)
    # not necessary, so it is commented
    ## test if a combined dataframe gets returned
    #def testCombinedDataFrame(self):
    #    # only printing the dataframe since this cannot be asserted using self.assert functions
    #    print(combined_df)
    # test if all the XBRL files have been downloaded
    #def testXBRLFiles(self):
    #    path = stock_data_obj.get_path()
    #    filepath = path + 'XBRL_19.xml'
    #    self.assertIs(os.path.exists(filepath), True)
    ## test if xml (for other years, 2019 in this case) has the relevant data, only to check if it has total equity
    #def test_is_data_adequate(self):
    #    raw_xml = stock_data_obj.get_financials_other_years()
    #    check_data_str = ':Equity '
    #    self.assertIn(check_data_str, raw_xml)
    # test if sp links list is valid
    def testSpLinksList(self):
        links_list = stock_data_obj.get_sp_links()
        self.assertNotEqual([], links_list)
        for link in links_list:
            self.assertIn("https://", link)
            self.assertIn(".xml", link)

    # test if all shareholding patterns xml files have been retrieved
    def testSPXML(self):
        stock_data_obj.write_shareholding_patterns()
        years = [18 + i for i in range(7)]
        path = 'data/' + stock + '/'
        for year in years:
            self.assertEqual(os.path.exists(path + 'SP_' + str(year) + '.xml'), True)

if __name__ == '__main__':
    unittest.main()
