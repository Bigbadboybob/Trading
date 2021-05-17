import requests
import yfinance as yf
import time
import yfinanceInfo
import os
import stockScraper
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

def yahooArticle(url):
    #do different things for one url or list of urls
    res = requests.get(url)
    res.raise_for_status()
    text = res.text
    s = text.index('pageCategory":"YFINANCE:')
    stockString = text[s + len('pageCategory":"YFINANCE:') : text.index('\"', s + len('pageCategory":"YFINANCE:'))]
    print(stockString)
    stocks = stockString.split(',')
    for t in stocks:
        time.sleep(1)
        stockScraper.daily(t)
        yfinanceInfo.baseInfo(t)

def yahooArticles(urls):
    for u in urls:
        yahooArticle(u)

articles = ['https://finance.yahoo.com/u/yahoo-finance/watchlists/the-autonomous-car',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/video-game-stocks',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/420_stocks',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/electronic-trading-stocks',
                 ]

def sharpe(stockName, days = 252, fileJson = True):
    stockScraper.daily(stockName)
    path = 'Data/Historical/' + stockName + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    return sharpeRatio(data, days, fileJson, stockName)
    
def sharpeRatio(data, days = 252, fileJson = True, stockName = ''):

    if (fileJson):
        path1 = 'Data/calcStats/' + stockName + '.json'
        if (os.path.exists(path1) and os.path.getsize(path1) > 2):
            jsonFile = open(path1, 'r')
            j = json.load(jsonFile)
            jsonFile = open(path1, 'w')
        else:
            jsonFile = open(path1, 'w')
            j = {}


    period = len(data.index)
    if (period > days):
        startDate = data.index[period - 1 - days]
    else:
        startDate = data.index[0]
        print('start date out of bounds')
    endDate = data.index[period - 1]
    years = days/252
    CAGR = (data.at[endDate, 'Close']/data.at[startDate, 'Close'])**(1/years) - 1
    riskFree = 0.0163
    #TODO: Eventually we wanna use expected return rather than CAGR
    
    data.insert(len(data.columns), 'Return', np.nan)
    for i in range(1, len(data.index)):
        prev = data['Close'][i - 1]
        curr = data['Close'][i]
        data['Return'][i] = (curr/prev) - 1
    std = data['Return'].std()
    aVol= std*np.sqrt(252)
    ret = (CAGR - riskFree)
    sharpe = ret/aVol
    
    if (fileJson):
        j['sharpe'] = sharpe
        json.dump(j, jsonFile)
        jsonFile.close()

    return (ret, aVol)

def tdSharpe(stock1, stock2, split = 100):
    yfinanceInfo.daily(stock1)
    path1 = 'Data/Historical/' + stock1 + '.csv'
    data1 = pd.read_csv(path1, index_col=0, parse_dates=True)

    yfinanceInfo.daily(stock2)
    path2 = 'Data/Historical/' + stock2 + '.csv'
    data2 = pd.read_csv(path2, index_col=0, parse_dates=True)

    retPoints = []
    aVolPoints = []
    for i in range(0, split + 1):
        data = data1*(i/split) + data2*(1-i/split)
        nLen = min(len(data1.index), len(data2.index))
        mLen = max(len(data1.index), len(data2.index))
        dropped = data.index[0:mLen - nLen]
        data = data.drop(dropped)
        ret, aVol = sharpeRatio(data, fileJson = False)
        retPoints.append(ret)
        aVolPoints.append(aVol)
    
    #points = pd.DataFrame(retPoints, aVolPoints, columns = ['ret', aVol])
    #path = 'Data/sample/' + 'tdSharpe.csv'
    #points.to_csv(path)
    
    plt.scatter(aVol, ret)


def ndSharpe(stocks):
    #TODO
    n=1


#Plot 2-D Sharpe Ratio
#points = pd.read_csv('Data/sample/' + 'tdSharpe.csv')
#print(points)
#ret = points['ret']
#aVol = points['aVol']
#plt.scatter(aVol, ret)
#plt.show()

#Gather articles
#yahooArticle('https://finance.yahoo.com/u/yahoo-finance/watchlists/the-autonomous-car')
#yfinanceInfo.plot("TSLA", "Close")
#yahooArticles(articles)
#sp = stockScraper.SPY()
#for s in sp:
#    time.sleep(1)
#    stockScraper.daily(t)
#    yfinanceInfo.baseInfo(t)


#earnings-netIncome
#shares-sharesOutstanding
#EPS-trailingEPS


