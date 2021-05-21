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

def price(stockName):
    yfinanceInfo.baseInfo(stockName)        
    pathj = 'Data/Info/' + stockName + '.json'
    jsonFile = open(pathj, 'r')
    j = json .load(jsonFile)
    price = j['regularMarketPrice']
    return price


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
            j = {}
            jsonFile = open(path1, 'w')


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

def tdSharpe(stock1, stock2, split = 100, days = 252):
    yfinanceInfo.daily(stock1)
    path1 = 'Data/Historical/' + stock1 + '.csv'
    data1 = pd.read_csv(path1, index_col=0, parse_dates=True)

    yfinanceInfo.daily(stock2)
    path2 = 'Data/Historical/' + stock2 + '.csv'
    data2 = pd.read_csv(path2, index_col=0, parse_dates=True)

    #dropping extra data
    days1 = len(data1.index)
    days2 = len(data2.index)
    if (days1 < 253 or days2 < 253):
        days = min(days1, days2)
    dropped1 = data1.index[0: days1 - days - 1]
    dropped2 = data2.index[0: days2 - days - 1]
    data1 = data1.drop(dropped1)
    data2 = data2.drop(dropped2)
    print('lets go')

    #In order to also get sharpe ratio json for individual stocks
    ret1, aVol1 = sharpeRatio(data1.copy(deep = True), stockName = stock1)
    ret2, aVol2 = sharpeRatio(data2.copy(deep = True), stockName = stock2)
    retPoints = [ret1, ret2]
    aVolPoints = [aVol1, aVol2]

    for i in range(1, split):
        data = data1*(i/split) + data2*(1-i/split)
        if (days < 252):
            ret, aVol = sharpeRatio(data, days = days, fileJson = False)
        else:
            ret, aVol = sharpeRatio(data, fileJson = False)
        retPoints.append(ret)
        aVolPoints.append(aVol)

    
    #points = pd.DataFrame(retPoints, aVolPoints, columns = ['ret', aVol])
    #path = 'Data/sample/' + 'tdSharpe.csv'
    #points.to_csv(path)
    
    plt.scatter(aVolPoints, retPoints)
    plt.show()
    #TODO: Return a list of sharpe frontier points
    #TODO: keep track of actual stock proportions

    #~0.115 seconds per year long sharpe calculation
    #2 seconds per dataset dropping data

def ndSharpe(stocks, days = 252):
    #TODO: add split param
    #TODO: keep track of actual stock proportions
    datas = []
    for s in stocks:
    #TODO: Account for missing data
        yfinanceInfo.daily(s)
        path = 'Data/Historical/' + s + '.csv'
        data = pd.read_csv(path1, index_col=0, parse_dates=True)
        datas.append(data)

    #dropping extra data
    dayss = []
    for d in datas:
        days = len(d.index)
        dayss.append(days)
    
    minD = min(dayss)
    if (minD < 253):
        days = days

    for d in datas:
        dropped = d.index[0: len(d.index) - days - 1]
        d = d.drop(dropped)

    #In order to also get sharpe ratio json for individual stocks
    retPoints = []
    aVolPoints = []
    for i in range(0, len(stocks)):
    #TODO: Account for missing data
        ret, aVol = sharpeRatio(datas[i].copy(deep = True), stockName = stocks[i])
        retPoints.append(ret)
        aVolPoints.append(aVol)

    #TODO: determine which splits of stocks to do
    for i in range(1, split):
        data = datas[0]*(i/split) + datas[1]*(1-i/split)
        if (days < 252):
            ret, aVol = sharpeRatio(data, days = days, fileJson = False)
        else:
            ret, aVol = sharpeRatio(data, fileJson = False)
        retPoints.append(ret)
        aVolPoints.append(aVol)
    
    #points = pd.DataFrame(retPoints, aVolPoints, columns = ['ret', aVol])
    #path = 'Data/sample/' + 'tdSharpe.csv'
    #points.to_csv(path)
    
    plt.scatter(aVolPoints, retPoints)
    plt.show()


def ndSharpeRatio(stocks, datas, split = 10):
    if (len(stocks) != len(datas)):
        print('ERROR: stocks and datas do no match')
    #TODO
    n=1

def cMovingAvg(stock, days = 90):
    yfinanceInfo.daily(stock)
    path = 'Data/Historical/' + stock + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    return cMoving(data, days = days)
    
def cMoving(data, days = 90):
    length = len(data.index)
    if (length < days):
        print('ERROR: data < moving avg period')
        return -1

    series = data.iloc[length-days:length]['Close']
    avg = series.sum()/days
    return avg

def movingAvg(stock, days = 90):
    yfinanceInfo.daily(stock)
    path = 'Data/Historical/' + stock + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    return moving(data, days)
    
def moving(data, days = 90):
    data.insert(len(data.columns), 'Avg', np.nan)

    series = data.iloc[0:days]['Close']
    avg = series.sum()/days
    data['Avg'][days] = avg
    for i in range(days + 1, len(data.index)):
        avg = avg - data['Close'][i-days]/90 + data['Close'][i]/90
        data['Avg'][i] = avg

    plot1 = plt.figure(1)
    data['Close'].plot()
    plot2 = plt.figure(2)
    data.iloc[days - 1:]['Avg'].plot()
    plt.show()
    #TODO: When you learn matplotlib plot these two at the same time




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


