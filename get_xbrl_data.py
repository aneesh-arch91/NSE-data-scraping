import pandas as pd
import xml.etree.ElementTree as ET
import browser_cookie3
import requests as rq
from datetime import datetime
import os
import sys
import io

class XBRLRetrieval:
    current_month = datetime.now().month
    current_year = datetime.now().year
    def __init__(self, stock, headers, cookies):
        self.stock = stock
        self.headers = headers
        self.cookies = cookies
        self.path = 'data/' + stock + '/'
        self.data_retrieval_successful = True
    # function to return data retrieval status
    def get_retrieval_status(self):
        return self.data_retrieval_successful
    # function to get the last 31 March
    @staticmethod
    def get_last_march():
        if (XBRLRetrieval.current_month > 3):
            year_str = str(XBRLRetrieval.current_year)[-2:]
        else:
            year_str = str(XBRLRetrieval.current_year - 1)[-2:]
        return 'Mar-' + year_str

    # function to return the path
    def get_path(self):
        return self.path
    # helper function to get the stock code.
    def get_stock_code(self):
        stock_df = pd.read_csv('data/Equity.csv')
        try:
            code = stock_df[stock_df['Security Id'] == self.stock].iloc[0]['Security Code']
        except IndexError:
            #temp_stock = input("Maybe the stock symbol on BSE is different? Enter the BSE stock symbol.")
            #code = stock_df[stock_df['Security Id'] == temp_stock].iloc[0]['Security Code']
            self.data_retrieval_successful = False
            print("Data unavailable on BSE! Aborting...")
            return
        return code
    
    # helper function to check if the links files are valid or they have tables
    @staticmethod
    def is_valid_html(html):
        try:
            pd.read_html(io.StringIO(html))
            return True
        except ValueError:
            return False

    # helper function to retry if the returned response is invalid
    def retry_if_invalid(self, url, filepath, validation_function, retry_count=5):
        raw_response = ''
        if (os.path.exists(filepath)):
            with open(filepath, 'r') as f:
                raw_reponse = f.read()
            if (validation_function(raw_reponse)):
                return 'Valid'
        response = rq.get(url, headers=self.headers, cookies=self.cookies)
        response.encoding = 'utf-8'
        raw_reponse = response.text
        retry_index = retry_count
        while(not validation_function(raw_reponse) and retry_index > 0):
            response = rq.get(url, headers=self.headers, cookies=self.cookies)
            response.encoding = 'utf-8'
            raw_reponse = response.text
            retry_index -= 1
        if (retry_index == 0 and not validation_function(raw_reponse)):
            print("File: ", filepath)
            print("Data incomplete! Aborting...")
            self.data_retrieval_successful = False
            return
        return raw_reponse
        
    # helper function to get the raw html from a link, function to get all links corresponding to the XBRL files 
    def get_raw_html(self, url, index):
        filepath = self.path + 'links' + str(index) + '.html'
        raw_html = self.retry_if_invalid(url, filepath, XBRLRetrieval.is_valid_html)
        if raw_html is None or raw_html == "Valid":
            return
        with open(self.path + 'links' + str(index) + '.html', 'w') as f:
            f.write(raw_html)

    # function to get all links files
    def get_all_link_files(self):
        code = self.get_stock_code()
        if (code is None):
            return
        url = 'https://www.bseindia.com/corporates/comp_results.aspx?Code=' + str(code)
        for i in range(5):
            self.get_raw_html(url + '&PID=' + str(i), i)

    # several helper functions
    @staticmethod
    def fix_columnnames(df):
        df.columns = [col[0] for col in df.columns]
    # removing na values from url
    @staticmethod
    def remove_na_values_url(df):
        df = df[~df['XBRL link'].str.contains('None')]
        return df
    @staticmethod
    def fix_the_columns(df):
        # remove nan from Quarter column
        df['Quarter'] = df['Quarter'].apply(lambda x: x[0])
        # remove NA values from Consolidated XBRL column
        #df.drop(df[df['Consolidate XBRL'] == ('-', None)].index, inplace=True)
        #df.drop(df[df['Standalone XBRL'] == ('-', None)].index, inplace=True)
        # removing the tuple and putting the link the XBRL column
        df['Consolidate XBRL'] = df['Consolidate XBRL'].apply(lambda x: str(x[1]))
        df['Standalone XBRL'] = df['Standalone XBRL'].apply(lambda x: str(x[1]))
        # changing the type column
        df['Type'] = df['Type'].apply(lambda x: x[0])
    @staticmethod
    def remove_useless_columns(df):
        df = df[['Quarter', 'XBRL link']]
        return df
    @staticmethod
    def remove_last_row(df):
        # dropping the last row
        df.drop(df.tail(1).index, inplace=True)
    @staticmethod
    def remove_last_year(df):
        df = df[~df['Quarter'].str.contains(XBRLRetrieval.get_last_march())]
        return df
    @staticmethod
    def filter_yearly(df):
        df = df[df['Quarter'].str.contains('-Mar-')]
        return df
        #df.drop(df[df['Type'] != 'Year'].index, inplace=True)
    # function to eliminate standalone xbrl if consolidated are present
    @staticmethod
    def prefer_consolidated(df):
        consolidated_df = df[df['Quarter'].str.contains('Consolidated')]
        if (not consolidated_df.empty):
            df = consolidated_df
            return 'Consolidated'
        return 'Standalone'
    @staticmethod
    def get_all_links(df):
        cut_four = lambda x: x[-2:]
        year_list = list(df['Quarter'].apply(cut_four))
        links_dict = dict(zip(year_list, list(df['XBRL link'])))
        return links_dict

    # helper function to manipulate the combined dataframe for use
    @staticmethod
    def fix_combined_df(df):
        XBRLRetrieval.fix_columnnames(df)
        # reset index
        df.reset_index(drop=True, inplace=True)
        XBRLRetrieval.fix_the_columns(df)
        # is the data standalone only?
        if (XBRLRetrieval.prefer_consolidated(df) == 'Standalone'):
            df['XBRL link'] = df['Standalone XBRL']
        else:
            df['XBRL link'] = df['Consolidate XBRL']
        df = XBRLRetrieval.remove_na_values_url(df)
        df = XBRLRetrieval.remove_useless_columns(df)
        df = XBRLRetrieval.filter_yearly(df)
        df = XBRLRetrieval.remove_last_year(df)
        df = df.drop_duplicates()
        df = df[:6]
        return df
        
    # function to return the combined dataframe
    def get_combined_df(self):
        df1 = pd.read_html(self.path + 'links0.html', skiprows=0, header=0, extract_links='body')[-1]
        combined_df = df1
        XBRLRetrieval.remove_last_row(combined_df)
        for i in range(1, 5):
            filepath = self.path + 'links' + str(i) + '.html'
            df = pd.read_html(filepath, skiprows=0, header=0, extract_links='body')[-1]
            XBRLRetrieval.remove_last_row(df)
            combined_df = pd.concat([combined_df, df], axis=0)
        combined_df = XBRLRetrieval.fix_combined_df(combined_df)
        return combined_df

    # function to download all but the latest XBRL files
    def download_xbrl_files(self):
        self.get_all_link_files()
        if (not self.data_retrieval_successful):
            return
        df = self.get_combined_df()
        urldict = XBRLRetrieval.get_all_links(df)
        if (len(urldict) < 6):
            print("Not enough links!")
            print("Data incomplete! Abort.")
            self.data_retrieval_successful = False
            return
        for year, url in urldict.items():
            filename = 'XBRL'+ "_" + str(int(year) - 1) +".xml"
            xml = self.retry_if_invalid(url, self.path + filename, XBRLRetrieval.is_xml_valid)
            if xml is None:
                break
            elif xml == 'Valid':
                continue
            with open(self.path + filename, "w") as f:
                f.write(xml)
                print(filename, " XBRL file downloaded")

    # A function to retrieve the integrated filings links for all stocks 
    def get_int_filings_file(self):
        filepath = 'data/int_filings.csv'
        if (not os.path.exists(filepath)):
            url_integrated_filings = "https://www.nseindia.com/api/integrated-filing-results?index=equities&csv=true&type=Integrated%20Filing-%20Financials"
            response = rq.get(url_integrated_filings, headers=self.headers, cookies=self.cookies)
            csv = response.content
            with open('data/int_filings.csv', 'wb') as f:
                f.write(csv)
        else:
            return
    # a function to return XML data from a previous year XBRL file
    def get_financials_other_years(self):
        filename = 'XBRL_19.xml'
        raw_xml = ''
        with open(self.path + filename, 'r') as f:
            raw_xml = f.read()
        return raw_xml

    # a helper function useful in selecting the most appropriate latest filings
    @staticmethod
    def get_latest_xbrl_url(df):
        #print(df[['CONSOLIDATED / STANDALONE \n', 'AUDITED / UNAUDITED \n', 'TYPE OF SUBMISSION \n']])
        #while (df.shape[0] > 1):
        if ('Consolidated' in df['CONSOLIDATED / STANDALONE \n'].unique()):
            df = df[df['CONSOLIDATED / STANDALONE \n'] != 'Standalone']
        if ('Audited' in df['AUDITED / UNAUDITED \n'].unique()):
            df = df[df['AUDITED / UNAUDITED \n'] != 'Un-Audited']
        if ('Revision' in df['TYPE OF SUBMISSION \n'].unique()):
            df = df[df['TYPE OF SUBMISSION \n'] != 'Original']
        return df['XBRL \n'].values[0]

    # function to check if xml is valid
    @staticmethod
    def is_xml_valid(xml):
        xml_check_str1 = '<?xml version="1.0" encoding="UTF-8"'
        check_data_str = ':Equity '
        return xml_check_str1 in xml and check_data_str in xml

    # function to check if shareholding xml is valid
    @staticmethod
    def is_xml_valid2(xml):
        xml_check_str1 = '<?xml version="1.0" encoding="UTF-8"'
        check_data_str = ':NumberOfShares '
        return xml_check_str1 in xml and check_data_str in xml

    # This function will take the stockname and return the latest financial results (integrated filing-financials) in XBRL XML format.
    def get_latest_financials_XML(self):
        data_dir = 'data/'
        int_file_path = data_dir + 'int_filings.csv'
        self.get_int_filings_file()
        xbrl_file_path = self.path + 'XBRL_24.xml'
        xbrl_df = pd.read_csv(int_file_path)
        xbrl_url_df = (xbrl_df.loc[(xbrl_df['SYMBOL \n'] == self.stock)
            & (xbrl_df['QUARTER END DATE \n'] == '31-MAR-2025')])
        if (xbrl_url_df.empty):
            print("File: ", 'XBRL_24.xml')
            print("Data incomplete! Aborting...")
            self.data_retrieval_successful = False
            return
        xbrl_url = XBRLRetrieval.get_latest_xbrl_url(xbrl_url_df) 
        raw_xml = self.retry_if_invalid(xbrl_url, xbrl_file_path, XBRLRetrieval.is_xml_valid)
        if raw_xml is None:
            return
        return raw_xml

    # write the latest XBRL data
    def write_latest_financials(self):
        raw_xml = self.get_latest_financials_XML()
        filepath = self.path + 'XBRL_24.xml'
        if (raw_xml is None or raw_xml == 'Valid'):
            return
        if (not os.path.exists(filepath)):
            with open(filepath, 'w') as f:
                f.write(raw_xml)
                print('latest XBRL file downloaded')

    @staticmethod
    def is_valid_csv(csv):
        html_str = '<!DOCTYPE html>'
        csv_str = 'PROMOTER & PROMOTER GROUP (A)'
        return html_str not in csv and csv_str in csv
    
    # a function to get the links list for the shareholding patterns csv files
    def get_sp_links(self):
        filename = 'promoters_share.csv'
        if (not os.path.exists(self.path + filename)):
            return
        xbrl_df = pd.read_csv(self.path + filename)
        xbrl_df = xbrl_df[xbrl_df['AS ON DATE'].str.contains('31-MAR-') & xbrl_df['ACTION'].str.contains('.xml')]
        links = xbrl_df['ACTION'].tolist()
        links = links[:7]
        links = list(reversed(links))
        return links

    def write_shareholding_patterns(self):
        xbrl_links = self.get_sp_links()
        if (len(xbrl_links) < 7):
            print("Data incomplete. Aborting...")
            self.data_retrieval_successful = False
            return
        else:
            for i in range(7):
                filename = 'SP_' + str(18 + i) + '.xml'
                xml = self.retry_if_invalid(xbrl_links[i], self.path + filename, XBRLRetrieval.is_xml_valid2)
                if (xml is None or xml == 'Valid'):
                    continue
                else:
                    print("File: ", filename, "downloaded")
                    with open(self.path + filename, 'w') as f:
                        f.write(xml)

    # A function to get promoters share from NSE shareholding patterns page
    def get_promoters_share(self):
        url = "https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&symbol=" + self.stock + "&csv=true"
        filename = 'promoters_share.csv'
        csv = self.retry_if_invalid(url, self.path + filename, XBRLRetrieval.is_valid_csv)
        if csv is None or csv == 'Valid':
            return
        with open(self.path + filename, 'w') as f:
            f.write(csv)
    # helper function
    # function to control the execution of a function based on a condition
    @staticmethod
    def abort_or_continue(condition, function):
        if (condition):
            function()
        else:
            return
    # A function to retrieve all XBRL files
    def get_all_xbrl_files(self):
        self.write_latest_financials()
        XBRLRetrieval.abort_or_continue(self.data_retrieval_successful, self.download_xbrl_files)
        XBRLRetrieval.abort_or_continue(self.data_retrieval_successful, self.get_promoters_share)
        XBRLRetrieval.abort_or_continue(self.data_retrieval_successful, self.write_shareholding_patterns)
