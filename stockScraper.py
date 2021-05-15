import requests
import sys
import csv
import os
import time
import math
import traceback

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
def historicalData(stockName):
    try:
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
        #print(downloadData)
        
        outFile = open('D:\\Code\\Python\\stock trading\\stockData\\historicalData\\'+ stockName+'History.csv', 'wb')
        outFile.write(dataFile.content)
        
        outFile.close()
        return True
    except Exception as e:
        print(stockName + 'historicalFail')
        print(traceback.format_exc())
        return False

print(advancedStats('F'))

#ask is buy price and bid is sell price and spread is the difference
#beta is volatility relative to the market. 1 indicates that the security's price moves with the market.
#A stock with a beta of 1.2 is 20% more volatile than the market. A beta of .65 is 35% less volatile.
#https://query1.finance.yahoo.com/v7/finance/download/TSLA?period1=1277769600&period2=1609891200&interval=1d&events=history&includeAdjustedClose=true
#https://query1.finance.yahoo.com/v7/finance/download/PLUG?period1=941155200&period2=1609891200&interval=1d&events=history&includeAdjustedClose=true
