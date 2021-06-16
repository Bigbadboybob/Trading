import requests
import sys
import csv
import os
import time
import math
import traceback
import json
import pandas as pd
import numpy as np
import datetime as dt

#TODO: research APIs and probably debug the indexing of HTML
#get this working for pandas dataframe structure and plot data
#add a test function which tests how well scraper is working and outputs percentage success

def nameURL(name):
    if 'https:' in name:
        stockURL = name
        stockName=stockURL[stockURL.index('=')+1:]
    else:
        stockName = name
        stockURL = 'https://finance.yahoo.com/quote/' + name + '?p=' + name
        statsURL = 'https://finance.yahoo.com/quote/' + name + '/key-statistics?p=' + name
        historyURL = 'https://finance.yahoo.com/quote/' + name + '/history?p=' + name
    return stockName, stockURL, statsURL, historyURL

def dataPoint(keyWord, dataText):
    keyWord = '\"'+keyWord+'\"'
    keyPos = dataText.index(keyWord)
    #check for no data
    if dataText[keyPos+len(keyWord)+3] == 'r':
        datum = dataText[keyPos+len(keyWord)+8 : dataText.index(',', keyPos)]
        return datum
    elif dataText[keyPos+len(keyWord)+3] == 'c':
        datum = dataText[keyPos+len(keyWord)+10 : dataText.index('\"', keyPos)]
        return datum
    else:
        return 'N/A'

#Summary Page
def baseStats(stockName):
    try:
        stockName = nameURL(stockName)[0]
        stockURL = nameURL(stockName)[1]
        res = requests.get(stockURL)
        res.raise_for_status()
        text = res.text

        dataStart = text.index('\"' + stockName + '\"' + ':{"sourceInterval":15,"quoteSourceName":"Delayed Quote",')
        
        dataText = text[dataStart: text.index('fullExchangeName', dataStart)]

        dataKeyWords = ['regularMarketOpen', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'sharesOutstanding', 'regularMarketDayHigh', 'regularMarketDayLow',
                        'regularMarketChange', 'fiftyTwoWeekHighChange', 'fiftyTwoWeekLowChange', 'regularMarketPrice', 'regularMarketVolume', 'marketCap' ]

        outFile = open('D:\\Code\\Python\\stock trading\\stockData\\stats\\'+ stockName+'Data.csv', 'w', newline='')
        outWriter = csv.writer(outFile)

        for d in dataKeyWords:
            outWriter.writerow([d, dataPoint(d, dataText)])
        #valuation
        try:
            valuationStart = text.rindex('valuation') + 37
            valuation = text[valuationStart : text.index('\"', valuationStart)]
            outWriter.writerow(['valuation', valuation])
        except Exception as e:
            outWriter.writerow(['valuation', 'error'])
            print(traceback.format_exc())
        outFile.close()
        return True
    except Exception as e:
        print(stockName + 'baseFail')
        print(traceback.format_exc())
        return False

#Stats Page
def advancedStats(stockName):
    try:
        if not baseStats(stockName):
            return False
        stockName = nameURL(stockName)[0]
        statURL = nameURL(stockName)[2]
        res = requests.get(statURL)
        res.raise_for_status()
        text = res.text

        outFile = open('D:\\Code\\Python\\stock trading\\stockData\\stats\\'+ stockName+'Stats.csv', 'w', newline='')
        outWriter = csv.writer(outFile)

        dataStart = text.index('defaultKeyStatistics')
        dataText = text[dataStart: text.index('currencySymbol', dataStart)]

        dataKeyWords = ['enterpriseToRevenue', 'beta3Year', 'profitMargins', 'enterpriseToEbitda', '52WeekChange', 'morningStarRiskRating', 'forwardEps', 'revenueQuarterlyGrowth',
                        'sharesOutstanding', 'fundInceptionDate', 'annualReportExpenseRatio', 'totalAssets', 'bookValue', 'sharesShort', 'sharesPercentSharesOut', 'fundFamily',
                        'lastFiscalYearEnd', 'heldPercentInstitutions', 'netIncomeToCommon', 'trailingEps', 'lastDividendValue', 'SandP52WeekChange', 'priceToBook', 'heldPercentInsiders',
                        'nextFiscalYearEnd', 'yield', 'mostRecentQuarter', 'shortRatio', 'sharesShortPreviousMonthDate', 'floatShares', 'beta', 'enterpriseValue', 'priceHint', 'threeYearAverageReturn',
                        'lastSplitDate', 'lastSplitFactor', 'legalType', 'lastDividendDate', 'morningStarOverallRating', 'earningsQuarterlyGrowth', 'priceToSalesTrailing12Months', 'dateShortInterest',
                        'pegRatio', 'ytdReturn', 'forwardPE', 'maxAge', 'lastCapGain', 'shortPercentOfFloat', 'sharesShortPriorMonth', 'impliedSharesOutstanding', 'fiveYearAverageReturn',
                        'financialsTemplate']

        for d in dataKeyWords:
            outWriter.writerow([d, dataPoint(d, dataText)])

        #VALUATIONS
        dataStart = text.index('QuoteTimeSeriesStore')
        dataTextFull = text[dataStart: text.index('UHAccountSwitchStore', dataStart)]

        dataKeys  = {'Market Cap' : '\"trailingMarketCap\"', 'enterpriseValue' : '\"quarterlyEnterpriseValue\"', 'Trailing P/E' : '\"trailingPeRatio\"', 'Forward P/E' : '\"trailingForwardPeRatio\"', 'PEG' : '\"trailingPegRatio\"',
                     'Price/Sales' : '\"trailingPsRatio\"', 'Price/Book' : '\"trailingPbRatio\"', 'enterprise Value/Revenue' : '\"trailingEnterprisesValueRevenueRatio\"', 'Enterprise Value/EBITDA' : '\"trailingEnterprisesValueEBITDARatio\"'}

        dataKeyWords  = ['Market Cap', 'enterpriseValue', 'Trailing P/E', 'Forward P/E', 'PEG', 'Price/Sales', 'Price/Book', 'enterprise Value/Revenue', 'Enterprise Value/EBITDA']

        #just finds current value
        for d in dataKeyWords:
            try:
                dataStart = dataTextFull.index(dataKeys[d])
                dataText = dataTextFull[dataStart: dataTextFull.index(']', dataStart)]
                #can't use dataPoint() because rindex()
                datumStart = dataText.rindex('\"raw\"')
                datum = dataText[datumStart + 6 : dataText.index(',', datumStart)]
                outWriter.writerow([d, datum])
            except ValueError:
                outWriter.writerow([d, 'N/A'])
        
        outFile.close()
        return True
    except Exception as e:
        if os.path.exists('D:\\Code\\Python\\stock trading\\stockData\\stats\\'+ stockName+'Data.csv'):
            os.remove('D:\\Code\\Python\\stock trading\\stockData\\stats\\'+ stockName+'Data.csv')
        print(stockName + 'advancedFail')
        print(traceback.format_exc())
        return False
    


#historical prices
def daily(stockName):
    #TODO: Optimize to only add new days if data already saved
    pathj = 'Data/calcStats/' + stockName + '.json'
    path = 'Data/Historical/'+ stockName + '.csv'
    if (os.path.exists(pathj) and os.path.getsize(pathj)>2):
        jsonFile = open(pathj, 'r')
        j = json .load(jsonFile)
        if (j.get('lastUpdate') == str(np.datetime64('today'))):
            data = pd.read_csv(path, parse_dates=True)
            return data
        jsonFile = open(pathj, 'w')
    else:
        j = {}
        jsonFile = open(pathj, 'w')
    stockName = nameURL(stockName)[0]
    historyURL = nameURL(stockName)[3]
    res = requests.get(historyURL)
    res.raise_for_status()
    text = res.text

    dateStart = text.index('\"firstTradeDate\"')
    firstDate = text[dateStart + 17 : text.index(',', dateStart + 17)]

    lastDate = str(int(math.floor(time.time()) )) 

    downloadData = 'https://query1.finance.yahoo.com/v7/finance/download/' + stockName + '?period1=' + firstDate + '&period2=' + lastDate + '&interval=1d&events=history&includeAdjustedClose=true'
    dataFile = requests.get(downloadData)
    
    outFile = open(path, 'wb')
    outFile.write(dataFile.content)
    outFile.close()

    data = pd.read_csv(path, parse_dates=True)
    today = data.tail(1).iloc[0]
    j['price'] = today['Close']
    j['lastUpdate'] = str(dt.date.today())
    try:
        json.dump(j, jsonFile)
        jsonFile.close()
    except Exception as e:
        print(traceback.format_exc())
        jsonFile.close()
        jsonFile = open(pathj, 'w')
        json.dump({}, jsonFile)
        jsonFile.close()
        return pd.DataFrame(index = ['Date', 'Open', 'High', 'Low', 'Close',
                                    'Adj Close', 'Volume'])
    return data



def SPY():
    try:
        res = requests.get('https://www.slickcharts.com/sp500',
                          headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'})
        res.raise_for_status()
        text = res.text
        outFile = open('Data/rawHTML/SPY.txt', 'w')
        outFile.write(text)

        outFile.close()
        start = text.index('table table-hover table-borderless table-sm')
        end = text.index('shadow p-3 mb-5 bg-white rounded', start)
        table = text[start : end]
        i = table.index('<a href="/symbol/')
        l = len('<a href="/symbol/')
        stockList = []
        while(i != -1):
            stockName = table[i + l : table.index('"', i + l)]
            stockName = stockName.replace('.', '-')
            stockList.append(stockName)

            i = table.find('<a href="/symbol/', table.index('"', i + l))
            i = table.find('<a href="/symbol/', i + l)
        return stockList
    except Exception as e:
        print('SPYFail')
        print(traceback.format_exc())
        return(stockList)

#print(daily('F'))
#print(daily('%5EGSPC'))


#ask is buy price and bid is sell price and spread is the difference
#beta is volatility relative to the market. 1 indicates that the security's price moves with the market.
#A stock with a beta of 1.2 is 20% more volatile than the market. A beta of .65 is 35% less volatile.
#https://query1.finance.yahoo.com/v7/finance/download/TSLA?period1=1277769600&period2=1609891200&interval=1d&events=history&includeAdjustedClose=true
#https://query1.finance.yahoo.com/v7/finance/download/PLUG?period1=941155200&period2=1609891200&interval=1d&events=history&includeAdjustedClose=true
