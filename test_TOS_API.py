
# importing alll the required library
import numpy as np  # The Numpy numerical computing library
import pandas as pd  # The Pandas data science library
import requests  # The requests library for HTTP requests in Python
import xlsxwriter  # The XlsxWriter libarary for
import math  # The Python math module
import time
import finnhub
# function nearestlevel to find which level is closest to Current Price


def nearestlevel(weekly_list, askPrice_value):
    difference = 1000000
    count = 0
    length = len(weekly_list)
    for elem in weekly_list:
        if abs(elem-askPrice_value) < difference:
            difference = abs(elem-askPrice_value)
            last_resistance = elem
            index = length-count
        count = count+1
    return last_resistance, index

# function resistance_rate to find whether the levels is Resistance or Support


def resistance_rate(askPrice_value, weekly_last_resistance):
    if ((weekly_last_resistance > askPrice_value*0.98) and weekly_last_resistance < (askPrice_value*1.01)):
        weekly_rate = abs(100-(askPrice_value/weekly_last_resistance*100))
    else:
        weekly_rate = 0
    if weekly_last_resistance > askPrice_value:
        rate_value = 'Resistance'
    else:
        rate_value = 'Support'
    return weekly_rate, rate_value


# function to get chunks of list
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# read the stocks from csv
stocks = pd.read_csv('SP500.csv')
stocks = stocks[:105]

# using Pandas library to define the titles
my_columns = ['Ticker', 'Price', 'Type', 'Index',
              'Resistance/Support',  'Gap_Percent', 'Levels']
final_dataframe = pd.DataFrame(columns=my_columns)
daily_dataframe = pd.DataFrame(columns=my_columns)

# Defining Finnhub API Key
finhub_client = finnhub.Client(api_key="c3jpdtaad3i82raojvqg")


# Created the symbol string with %2C attached to match the TD Ameritrade API's url
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append('%2C'.join(symbol_groups[i]))

batch_api_call_url = "https://api.tdameritrade.com/v1/marketdata/quotes?apikey=J7I6RHSE8U2WOGTWQ1IRF8X1JC494UHO&symbol=AAPL%2CMSFT%2CAMZN%2CGOOG%2CGOOGL%2CFB%2CBRK.B%2CTSLA%2CBRK.A%2CTSM%2CBABA%2CNVDA%2CV%2CJPM%2CUNH%2CMA%2CPYPL%2CHD%2CBAC%2CPG%2CDIS%2CADBE%2CCMCSA%2CNKE%2CXOM%2CORCL%2CNFLX%2CVZ%2CINTC%2CCRM%2CCSCO%2CT%2CCVX%2CTMUS%2CUPS%2CCOST%2CWFC%2CTXN%2CMCD%2CQCOM%2CC%2CINTU%2CSBUX%2CBABA%2CBLK%2CAXP%2CSCHW%2CIBM%2CGS%2CTGT%2CGE%2CNOW%2CAMD%2CSQ%2CCVS%2CSNAP%2CGM%2CFDX%2CDELL%2CCOF%2CTWLO%2CVMW%2CWMT%2CF%2CTWTR%2CEBAY%2CCMG%2CMAR%2CBK%2CORLY%2CWBA%2CEA%2CAAL%2CLVS%2CDFS%2CHPQ%2CEFX%2CBBY%2CDAL%2CDLTR%2CPAYC%2CCLX%2CZ%2CCZR%2CRCL%2CMGM%2CHPE%2CDPZ%2CNTAP%2CBA%2CRTX%2CLMT%2CLUV%2CF%2CSYF%2CSYY%2CKR%2CWM%2CSHOP%2CTDOC"
data = requests.get(batch_api_call_url).json()

# Getting the stocks price, levels for both daily and weekly, and calculate rate putting them into dataframes
count = 0
for symbol_string in symbol_strings:
    #batch_api_call_url = f'https://api.tdameritrade.com/v1/marketdata/quotes?apikey=J7I6RHSE8U2WOGTWQ1IRF8X1JC494UHO&symbol={symbol_string}'
    #data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split('%2C'):
        askPrice_value = data[symbol]['lastPrice']
        weekly_resistance_value = finhub_client.support_resistance(symbol, 'W')
        print(symbol)
        weekly_list = weekly_resistance_value['levels']
        [weekly_last_resistance, weekly_index] = nearestlevel(
            weekly_list, askPrice_value)
        daily_resistance_value = finhub_client.support_resistance(symbol, 'D')
        daily_list = daily_resistance_value['levels']
        [daily_last_resistance, daily_index] = nearestlevel(
            daily_list, askPrice_value)
        count = count+1
        if count % 29 == 0:
            time.sleep(40)
        [weekly_rate, rate_value] = resistance_rate(
            askPrice_value, weekly_last_resistance)
        [daily_rate, daily_rate_value] = resistance_rate(
            askPrice_value, daily_last_resistance)

        final_dataframe = final_dataframe.append(
            pd.Series([symbol,
                       askPrice_value, rate_value, weekly_index, weekly_last_resistance,
                       weekly_rate, weekly_list],
                      index=my_columns),
            ignore_index=True)
        daily_dataframe = daily_dataframe.append(
            pd.Series([symbol,
                       askPrice_value, daily_rate_value, daily_index, daily_last_resistance,
                      daily_rate, daily_list],
                      index=my_columns),
            ignore_index=True)

# filtering dataframes that removes the gap percentage greater than 3%
final_dataframe = final_dataframe[final_dataframe.Gap_Percent != 0]
daily_dataframe = daily_dataframe[daily_dataframe.Gap_Percent != 0]
# sorting the dataframes based on the levels index. This is because I like stocks with in between levels
final_dataframe = final_dataframe.sort_values(
    by='Index', ascending=False)
daily_dataframe = daily_dataframe.sort_values(
    by='Index', ascending=False)
# final_dataframe=final_dataframe[final_dataframe.isnone().any(axis=1)]
# daily_dataframe = daily_dataframe[(daily_dataframe.Index > 1) | (
#   daily_dataframe.Type != "Support")]

# creating an excel sheets to get dataframes in sheets
writer = pd.ExcelWriter('test_API.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(
    writer, sheet_name='Weekly Support and Resistance', index=False)

daily_dataframe.to_excel(
    writer, sheet_name='Daily Support and Resistance', index=False)

writer.save()
