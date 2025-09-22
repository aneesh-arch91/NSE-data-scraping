import requests as rq
import browser_cookie3
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import os
from bs4 import BeautifulSoup
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import sys

class OrganizeData:
    years = [2018 + x for x in range(7)]
    def __init__(self, stock, headers, cookies):
        self.stock = stock
        self.headers = headers
        self.cookies = cookies
        self.path = 'data/' + stock + '/'
        trees = {}
        for file in os.listdir(self.path):
            if file.startswith("XBRL_"):
                tree = ET.parse(self.path + file)
                year = file[-6:-4]
                trees[year] = tree
        trees = dict(sorted(trees.items())) 
        self.trees = list(trees.values())

        sp_trees = {}
        for file in os.listdir(self.path):
            if file.startswith("SP_"):
                tree = ET.parse(self.path + file)
                year = file[-6:-4]
                sp_trees[year] = tree
        sp_trees = dict(sorted(sp_trees.items())) 
        self.sp_trees = list(sp_trees.values())

    # function to get stock data status
    def get_data_status(self):
        filename = 'statusfile'
        status = ''
        with open(self.path + filename, 'r') as f:
            status = f.read()
        return status == 'Success'
    # function to remove commas from a list of strings
    @staticmethod
    def remove_commas(string):
        return string.replace(",", "")
    
    def get_shareholders_equity(self):
        se_list = [] 
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}Equity")):
                    se_list.append(int(child.text))
        return se_list
    
    def get_profit_after_tax(self):
        pat_list = [] 
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}ProfitLossForPeriod") and child.attrib['contextRef'] == 'FourD'):
                    pat_list.append(int(child.text))
        return pat_list
    
    def get_return_on_equity(self):
        pat_list = self.get_profit_after_tax()
        s_equity_list = self.get_shareholders_equity()
        return [(int(x) / int(y))*100 for x, y in zip(pat_list, s_equity_list)]
    
    # getting the profit before tax 
    # this function will be used for screener.in
    #def get_profit_before_tax(soup):
    #    # find the section with profit-loss table
    #    section = soup.find("section", id="profit-loss")
    #    # Now getting the net profit.
    #    profit_section = section.find_all("tr", class_="strong")
    #    pbt = profit_section[-2]
    #    # Last five years of net profit (after tax)
    #    last_profits = pbt.find_all("td")[-12:]
    #    last_profit_numbers = [td.text for td in last_profits]
    #    # Now removing the comma from these numbers
    #    pbt_last_years = [remove_commas(x) for x in last_profit_numbers]
    #    return pbt_last_years 
    # now the function for bse or nse xbrl files
    def get_profit_before_tax(self):
        pbt_list = [] 
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}ProfitBeforeTax") and child.attrib['contextRef'] == 'FourD'):
                    pbt_list.append(int(child.text))
        return pbt_list
    
    def get_total_interest(self):
        total_interest_list = []
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}FinanceCosts") and child.attrib['contextRef'] == 'FourD'):
                    total_interest_list.append(int(child.text))
        return total_interest_list
    
         
    # getting earnings before interest and tax
    def get_EBIT(self):
        total_interest = self.get_total_interest()
        pbt = self.get_profit_before_tax()
        return [sum((x,y)) for x, y in zip(total_interest, pbt)]
    
    #def get_avg_capital_employed(soup):
    #    capital_employed = get_capital_employed(soup) 
    #    avg_capital_employed = [capital_employed[0]]
    #    for i in range(1, len(capital_employed)):
    #        avg = (capital_employed[i] + capital_employed[i-1]) / 2
    #        avg_capital_employed.append(avg)
    #    return avg_capital_employed
    
    def get_return_on_capital_employed(self):
        EBIT = self.get_EBIT()
        capital_employed = self.get_capital_employed()
        #capital_employed = get_capital_employed(soup)
        #capital_employed = get_avg_capital_employed(soup)
        return [(int(x) / int(y))*100 for x, y in zip(EBIT, capital_employed)]
    
    
    def get_total_assets(self):
        total_asset_list = [] 
        #for i in range(len(trees)):
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}Assets")):
                    total_asset_list.append(float(child.text))
        return total_asset_list
    
    def get_current_liabilities(self):
        current_liabilities_list = []
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}CurrentLiabilities")):
                    current_liabilities_list.append(float(child.text))
        return current_liabilities_list
    
    def get_capital_employed(self):
        total_assets = self.get_total_assets() 
        current_liabilities = self.get_current_liabilities()
        return [(int(x) - int(y)) for x, y in zip(total_assets, current_liabilities)]
    
    def get_total_liabilities(self):
        total_liabilities_list = []
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}Liabilities")):
                    total_liabilities_list.append(float(child.text))
        return total_liabilities_list
    
    def get_debt_to_equity_ratio(self):
        shareholders_equity = self.get_shareholders_equity()
        total_liabilities = self.get_total_liabilities()
        #current_liabilities = get_current_liabilities(trees)
        return [(float(x)/ float(y)) for x, y in zip(total_liabilities, shareholders_equity)]
    
    def get_sales(self):
        total_sales_list = []
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}RevenueFromOperations") and child.attrib['contextRef'] == 'FourD'):
                    total_sales_list.append(int(child.text))
        return total_sales_list
         
    @staticmethod
    def get_cagr(ending_value, beginning_value, years):
        return ((ending_value/beginning_value)**(1/years) - 1) * 100
    
    #def get_cagr_sales(self):
    #    sales = self.get_sales()
    #    n = len(sales)
    #    return [OrganizeData.get_cagr(sales[i], sales[i - 1], 1) for i in reversed(range(n - 7, n))]
    def get_cagr_sales(self):
        sales = self.get_sales()
        n = len(sales)
        return [OrganizeData.get_cagr(sales[i], sales[i - 3], 3) for i in reversed(range(n - 4, n))]
    
    def get_cagr_profit(self):
        profit_list = self.get_profit_after_tax()
        n = len(profit_list)
        return [OrganizeData.get_cagr(profit_list[i], profit_list[i - 2], 2) for i in reversed(range(n - 5, n))]
    
    def get_abs_return_next_year(self, year):
        filename_begin = 'price_' + str(year) + "_1_" + '.csv'
        filename_end = 'price_' + str(year) + "_2_" + '.csv'
        begin_price_df = pd.read_csv(self.path + filename_begin)
        end_price_df = pd.read_csv(self.path + filename_end)
        begin_price_close = str(begin_price_df['close '].loc[0])
        end_price_close = str(end_price_df['close '].loc[0])
        # begin close price
        bcp = float(begin_price_close.replace(',', ''))
        # end close price
        ecp = float(end_price_close.replace(',', ''))
        return (ecp - bcp) / bcp * 100
    
    def get_absolute_return(self):
        years = [2018 + x for x in range(7)]
        abs_ret = []
        for year in years:
            #abs_ret.append(self.get_abs_return_next_year(year))
            if (self.get_abs_return_next_year(year) > 20):
                abs_ret.append(1)
            else:
                abs_ret.append(0)
        return abs_ret

    @staticmethod
    def categorize_absolute_return(df):
        df['Returns'] = np.where(df['Absolute Return Next Year'] > 0.2, '1', '0')
        return df

    def get_promoters_pledged_share(self):
        filename = 'promoters_share.csv'
        #promoters_share_df = pd.read_csv(self.path + filename)
        #promoters_share_df.drop(promoters_share_df[~(promoters_share_df['AS ON DATE'].str.contains('-MAR-'))].index, inplace=True)
        #promoters_share_df = promoters_share_df[:7]
        #promoters_share_list = promoters_share_df['PROMOTER & PROMOTER GROUP (A)'].to_list()
        return promoters_share_list

    def get_earnings_per_share(self):
        eps_list = []
        for tree in self.trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}DilutedEarningsLossPerShareFromContinuingAndDiscontinuedOperations") and child.attrib['contextRef'] == 'FourD'):
                    eps_list.append(float(child.text))
        return eps_list
        
    # get P.E ratio
    def get_price_to_earnings_ratio(self):
        bcp_list = []
        eps_list = self.get_earnings_per_share()
        pe_list = []
        for i in range(7):
            filename_begin = 'price_' + str(OrganizeData.years[i]) + "_1_" + '.csv'
            begin_price_df = pd.read_csv(self.path + filename_begin)
            begin_price_close = str(begin_price_df['close '].loc[0])
            bcp = float(begin_price_close.replace(',', ''))
            if (eps_list[i] == 0):
                if (pe_list == []):
                    pe_list.append(-1)
                else:
                    pe_list.append(np.mean(pe_list))
                continue
            pe_list.append(bcp / eps_list[i])
        return pe_list
        
        
    @staticmethod
    def normalize_percentage(data_list):
        return [float (x/100) for x in data_list]
    @staticmethod
    def normalize_de_ratio(de_ratio):
        return [x - 1.0 for x in de_ratio]
    # outlliers can distort the model
    @staticmethod
    def remove_outliers(df):
        df = df[(df['Absolute Return Next Year'] < 2) & (df['Absolute Return Next Year'] > -1)]
        return df
            
    @staticmethod
    def avg_three(num1, num2, num3): return (num1 + num2 + num3) / 3
    # new features as per Prasenjit Paul's book
    @staticmethod
    def last_three_avg(variable):
        return [OrganizeData.avg_three(variable[i], variable[i - 1], variable[i - 2]) for i in range(2, len(variable))]
    # min max normalization
    def min_max_normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    def get_promoters_pledge(self):
        pp_list = []
        flag = 0
        for tree in self.sp_trees:
            root = tree.getroot()
            for child in root:
                if (child.tag.endswith("}PledgedOrEncumberedSharesHeldAsPercentageOfTotalNumberOfShares") and child.attrib['contextRef'] == 'ShareholdingOfPromoterAndPromoterGroupI'):
                    flag = 1
                    pp_list.append(float(child.text))
            if (flag == 0):
                pp_list.append(0.0)
        return pp_list

    def get_financials_df(self):
        years = [2020, 2021, 2022, 2023, 2024]
        financials_df = pd.DataFrame(index=years, columns=['ROE', 'ROCE', 'D/E ratio', 'Promoters Share', 'CAGR Sales', 'P.E ratio', 'Absolute Return Next Year'], dtype=float)
        # if the data is not complete
        if (not self.get_data_status()):
            financials_df.drop('Absolute Return Next Year', axis=1, inplace=True)
            return financials_df.iloc[0:0]
        roe_list        = OrganizeData.last_three_avg(self.get_return_on_equity())
        roce_list       = OrganizeData.last_three_avg(self.get_return_on_capital_employed())
        de_ratio        = self.get_debt_to_equity_ratio()[2:]
        promoters_share = self.get_promoters_share()[2:]
        cagr_sales      = self.get_cagr_sales()
        #cagr_profit     = self.get_cagr_profit()
        pe_list = OrganizeData.last_three_avg(self.get_price_to_earnings_ratio())
        absolute_return = self.get_absolute_return()[2:]
        try:
            financials_df['ROE']                       = OrganizeData.normalize_percentage(roe_list)
            financials_df['ROCE']                      = OrganizeData.normalize_percentage(roce_list)
            financials_df['D/E ratio']                 = OrganizeData.normalize_de_ratio(de_ratio)
            financials_df['Promoters Share']           = OrganizeData.normalize_percentage(promoters_share)
            financials_df['CAGR Sales']                = OrganizeData.normalize_percentage(cagr_sales)
            financials_df['P.E ratio']                 = pe_list
            financials_df['P.E ratio']                 = OrganizeData.min_max_normalize(financials_df['P.E ratio'])
            #financials_df['CAGR Profit']               = OrganizeData.normalize_percentage(cagr_profit)
            financials_df['Absolute Return Next Year'] = OrganizeData.normalize_percentage(absolute_return)
            #financials_df['Absolute Return Next Year'] = absolute_return
        except ValueError:
            financials_df.drop('Absolute Return Next Year', axis=1, inplace=True)
            print('Data incomplete!!')
            return financials_df.iloc[0:0]
        # drop last row
        financials_df.drop(financials_df.tail(1).index, inplace=True)
        # remove outliers
        financials_df = OrganizeData.remove_outliers(financials_df)
        financials_df = OrganizeData.categorize_absolute_return(financials_df)
        #financials_df.drop(['Absolute Return Next Year'], axis=1, inplace=True)
        financials_df.drop('Absolute Return Next Year', axis=1, inplace=True)
        return financials_df

    # helper functions
    def get_roe_roce_category(self):
        roe_list = self.get_return_on_equity()
        roce_list = self.get_return_on_capital_employed()
        roe_roce_list = []
        for i in range(3, 7):
            if (OrganizeData.avg_three(roe_list[i-3], roe_list[i-2], roe_list[i-1]) > 20 and
                OrganizeData.avg_three(roce_list[i-3], roce_list[i-2], roce_list[i-1]) > 20 and
                (roe_list[i] < roe_list[i-1] < roe_list[i-2]) and 
                (roce_list[i] < roce_list[i-1] < roce_list[i-2])
                ):
                roe_roce_list.append(1)
            else:
                roe_roce_list.append(0)
        return roe_roce_list
    
    # function to categorize the D/E ratio as per the PP book
    def get_de_ratio_category(self):
        de_list = self.get_debt_to_equity_ratio()
        new_de_list = []
        for i in range(3, 7):
            if (OrganizeData.avg_three(de_list[i-1], de_list[i-2], de_list[i-3]) < 1 or
                (1 > de_list[i] < de_list[i-1] < de_list[i-2])
                ):
                new_de_list.append(1)
            else:
                new_de_list.append(0)
        return new_de_list
    # function to categorize the promoters pledge
    def get_pp_category(self):
        pp_list = self.get_promoters_pledge()
        pp_category = []
        for i in range(3, 7):
            if (OrganizeData.avg_three(pp_list[i-1], pp_list[i-2], pp_list[i-3]) < 10 or
                (11 > pp_list[i] < pp_list[i-1] < pp_list[i-2])
                ):
                pp_category.append(1)
            else:
                pp_category.append(0)
        return pp_category

    # function to categorize the cagr sales
    def get_cagr_sales_category(self):
        cagr_sales_list = self.get_cagr_sales()
        new_sales_list = []
        for i in range(4):
            if (cagr_sales_list[i] > 10):
                new_sales_list.append(1)
            else:
                new_sales_list.append(0)
        return new_sales_list
    # function to categorize the new p.e ratio
    def get_pe_ratio_category(self):
        pe_list = self.get_price_to_earnings_ratio()
        new_pe_list = []
        for i in range(3, 7):
            pe_avg = OrganizeData.avg_three(pe_list[i-1], pe_list[i-2], pe_list[i-3])
            if (pe_avg > pe_list[i] or
                np.abs(pe_list[i] - pe_avg) < 2):
                new_pe_list.append(1)
            else:
                new_pe_list.append(0)
        return new_pe_list

    def get_financials_halecs(self):
        years = [2020 + i for i in range(4)]
        df = pd.DataFrame(index=years, columns=['ROE_ROCE', 'D/E ratio', 'Promoters Pledge', 'CAGR Sales', 'P.E ratio', 'Returns'], dtype=float)
        if (not self.get_data_status()):
            print("Data incomplete!")
            df.drop('Returns', axis=1, inplace=True)
            return df.iloc[0:0]
        df['ROE_ROCE'] = self.get_roe_roce_category()
        df['D/E ratio'] = self.get_de_ratio_category()
        df['Promoters Pledge'] = self.get_pp_category()
        df['CAGR Sales'] = self.get_cagr_sales_category()
        df['P.E ratio'] = self.get_pe_ratio_category()
        df['Returns'] = self.get_absolute_return()[3:]
        return df
    # function to categorize the ROE and ROCE together as instructed by the PP book
    #def get_financials_halecs(self, df):
    #    years = [2020, 2021, 2022, 2023, 2024]
    #    df = pd.DataFrame(index=years, columns=['ROE_ROCE', 'D/E ratio', 'Promoters Share', 'CAGR Sales', 'P.E ratio', 'Absolute Return Next Year'], dtype=float)
    #    # if the data is not complete
    #    if (not self.get_data_status()):
    #        df.drop('Absolute Return Next Year', axis=1, inplace=True)
    #        return financials_df.iloc[0:0]
    #    roe_list        = self.get_return_on_equity()
    #    roce_list       = self.get_return_on_capital_employed()
    #    de_ratio        = self.get_debt_to_equity_ratio()[2:]
    #    promoters_pledge = self.get_promoters_pledge()
    #    cagr_sales      = self.get_cagr_sales()
    #    pe_list = self.get_price_to_earnings_ratio()
    #    absolute_return = self.get_absolute_return()[2:]

    #    roe_roce_list = OrganizeData.roe_roce_category(roe_list, roce_list)
    #    new_de_list = OrganizeData.de_ratio_category(de_ratio)
    #    new_pe_list = OrganizeData.categorize_pe_ratio(promoters_pledge)
    #    new_sales_list = OrganizeData.categorize_cagr_sales(cagr_sales)
    #    try:
    #        financials_df['ROE']                       = OrganizeData.normalize_percentage(roe_list)
    #        financials_df['ROCE']                      = OrganizeData.normalize_percentage(roce_list)
    #        financials_df['D/E ratio']                 = OrganizeData.normalize_de_ratio(de_ratio)
    #        financials_df['Promoters Share']           = OrganizeData.normalize_percentage(promoters_share)
    #        financials_df['CAGR Sales']                = OrganizeData.normalize_percentage(cagr_sales)
    #        financials_df['P.E ratio']                 = pe_list
    #        financials_df['P.E ratio']                 = OrganizeData.min_max_normalize(financials_df['P.E ratio'])
    #        #financials_df['CAGR Profit']               = OrganizeData.normalize_percentage(cagr_profit)
    #        financials_df['Absolute Return Next Year'] = OrganizeData.normalize_percentage(absolute_return)
    #        #financials_df['Absolute Return Next Year'] = absolute_return
    #    except ValueError:
    #        financials_df.drop('Absolute Return Next Year', axis=1, inplace=True)
    #        print('Data incomplete!!')
    #        return financials_df.iloc[0:0]
    #    # drop last row
    #    financials_df.drop(financials_df.tail(1).index, inplace=True)
    #    # remove outliers
    #    #financials_df = OrganizeData.remove_outliers(financials_df)
    #    financials_df = OrganizeData.categorize_absolute_return(financials_df)
    #    #financials_df.drop(['Absolute Return Next Year'], axis=1, inplace=True)
    #    financials_df.drop('Absolute Return Next Year', axis=1, inplace=True)
    #    return financials_df
    #    #years = [2018 + x for x in range(7)]
    #    roe_list        = self.get_return_on_equity()
    #    roce_list       = self.get_return_on_capital_employed()
    #    de_ratio        = self.get_debt_to_equity_ratio()
    #    promoters_pledge = self.get_promoters_pledge()
    #    cagr_sales      = self.get_cagr_sales()
    #    #cagr_profit     = self.get_cagr_profit()
    #    pe_list = self.get_price_to_earnings_ratio()
    #    absolute_return = self.get_absolute_return()

    #    roe_roce_list = OrganizeData.roe_roce_category(roe_list, roce_list)
    #    new_de_list = OrganizeData.de_ratio_category(de_ratio)
    #    new_pe_list = OrganizeData.categorize_pe_ratio(promoters_pledge)
    #    new_sales_list = OrganizeData.categorize_cagr_sales(cagr_sales)
    #    df['ROE_ROCE'] = roe_roce_list
    #    return financials_df

#url = 'https://www.screener.in/company/' + stock + '/consolidated/'
#response = rq.get(url, headers=headers, cookies=cookies)
#res_html = response.text
#with open(stock + '_screener.html', 'w') as f:
#    f.write(res_html)
#res_html = None
#with open(stock + '_screener.html', 'r') as f:
#    res_html = f.read()
#soup = BeautifulSoup(res_html, 'html.parser')

# function to get the trees from the xml files
#def get_trees():
#    trees = {}
#    for file in os.listdir("./"):
#        if file.endswith(".xml"):
#            tree = ET.parse(file)
#            year = file[-6:-4]
#            trees[year] = tree
#    return dict(sorted(trees.items())) 
#trees_dict = get_trees()
#trees = list(get_trees().values())
#for i in range(len(trees)):
#    root = trees[i].getroot()
#    for child in root:
#        print(child.tag, child.text)


#print(get_financials_df(soup, trees))
#print(get_shareholders_equity(soup))
#test_all_functions(soup, trees)
#sys.exit()

# %% [markdown]
# Now, that we have all the data, let's train a basic machine learning model.
# X = {ROE, ROCE, D/E Ratio, Promoters Share, CAGR Sales, CAGR Profit}
# Y = {Absolute Return Next Year}

# %% [markdown]
# Assigning the data to a variable

# %%
#financials_df = get_financials_df(soup, trees)
#print(financials_df)
#X = financials_df.drop(['Absolute Return Next Year'], axis=1)
#y = financials_df[['Absolute Return Next Year']].values.ravel()
#
## %% [markdown]
## Splitting the data into train, test.
#
## %%
#X_train = X[:-2]
#y_train = y[:-2]
#X_test = X[-2:]
#y_test = y[-2:]
##print(X_train, X_test, y_train, y_test)
##X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.285, random_state=108)
#
## %% [markdown]
## Training the Linear Regression model
#
## %%
##reg = LinearRegression().fit(X_train, y_train)
#reg = RandomForestRegressor().fit(X_train, y_train)
#y_pred = reg.predict(X_test)
#print(y_pred)
#print(r2_score(y_test, y_pred))
