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
import datetime as dt
import random

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

def daily(stockName):
    data = yfinanceInfo.daily(stockName)
    #maybe <= 0?
    if data.index.size <= 1:
        data = stockScraper.daily(stockName)
    return data


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
    
def sharpeRatio(data, days = 252, fileJson = False, stockName = ''):

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
    startDate = data.index[period - 1 - days]
    endDate = data.index[period - 1]
    years = days/252
    CAGR = (data.at[endDate, 'Close']/data.at[startDate, 'Close'])**(1/years) - 1
    riskFree = 0.0163
    #TODO: Eventually we wanna use expected return rather than CAGR
    
    data.insert(len(data.columns), 'Return', np.nan)
    for i in range(period - 1 - days, period - 1):
        prev = data['Close'][i - 1]
        curr = data['Close'][i]
        data['Return'][i] = (curr/prev) - 1
    #print(data['Return'])
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

    #In order to also get sharpe ratio json for individual stocks
    ret1, aVol1 = sharpeRatio(data1.copy(deep = True), stockName = stock1)
    ret2, aVol2 = sharpeRatio(data2.copy(deep = True), stockName = stock2)
    retPoints = [ret1, ret2]
    aVolPoints = [aVol1, aVol2]
    ratios = [ret1/aVol1, ret2/aVol2]

    for i in range(1, split):
        data = data1*(i/split) + data2*(1-i/split)
        if (days < 252):
            ret, aVol = sharpeRatio(data, days = days, fileJson = False)
        else:
            ret, aVol = sharpeRatio(data, fileJson = False)
        retPoints.append(ret)
        aVolPoints.append(aVol)
        ratios.append(ret/aVol)

    print(ratios)
    plt.scatter(aVolPoints, retPoints, c = ratios, cmap = 'summer')
    cbar = plt.colorbar()
    cbar.set_label('Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Returns')
    plt.show()
    #TODO: Return a list of sharpe frontier points
    #TODO: keep track of actual stock proportions

    #~0.115 seconds per year long sharpe calculation
    #2 seconds per dataset dropping data

#tdSharpe('AAPL', 'GOOG')

def npSharpeRatio(data, fileJson = False, stockName = ''):

    if (fileJson):
        path1 = 'Data/calcStats/' + stockName + '.json'
        if (os.path.exists(path1) and os.path.getsize(path1) > 2):
            jsonFile = open(path1, 'r')
            j = json.load(jsonFile)
            jsonFile = open(path1, 'w')
        else:
            j = {}
            jsonFile = open(path1, 'w')

    #print('NP Data')
    #print(data)
    years = data.size/252
    CAGR = (data[data.size - 1]/data[0])**(1/years) - 1
    riskFree = 0.0163
    #TODO: Eventually we wanna use expected return rather than CAGR
    
    returns = np.empty(data.size - 1)
    for i in range(1, data.size):
        prev = data[i-1]
        curr = data[i]
        returns[i - 1] = (curr/prev) - 1
    #print(returns)
    std = returns.std()
    aVol= std*np.sqrt(252)
    ret = (CAGR - riskFree)
    sharpe = ret/aVol
    
    if (fileJson):
        j['sharpe'] = sharpe
        json.dump(j, jsonFile)
        jsonFile.close()

    return (ret, aVol)

def ndSharpe(stocks, days = 252, res = 100):
    #TODO: keep track of actual stock proportions
    datas = np.empty((0, days + 1))
    for s in stocks:
        yfinanceInfo.daily(s)
        path = 'Data/Historical/' + s + '.csv'
        data = pd.read_csv(path, index_col=0, parse_dates=True)
        data = data['Close'].to_numpy()
        data = data[data.size - days - 1 : data.size]
        datas = np.vstack((datas, data))

    #In order to also get sharpe ratio json for individual stocks
    retPoints = []
    aVolPoints = []
    maxSharpe = 0
    points = np.empty((0, len(stocks)))
    for i in range(0, len(stocks)):
        point = np.zeros(len(stocks))
        point[i] = 1
        points = np.vstack((points, point))
        ret, aVol = npSharpeRatio(datas[i], fileJson = True, stockName = stocks[i])
        retPoints.append(ret)
        aVolPoints.append(aVol)
        sharpe = ret/aVol
        if (sharpe > maxSharpe):
            maxSharpe = sharpe
            maxPoint = point

    for i in range(0, res):
        sPoint = np.zeros(len(stocks))
        #stars and bars to choose point with uniform probability distribution
        bars = random.sample(range(1, res + len(stocks) - 1), len(stocks) - 1)
        bars.sort()
        #for final stock/coord
        bars.append(res + len(stocks))
        prev = 0
        testList = [0 for i in range(0, res + len(stocks))]
        for i in range(0, len(bars)):
            testList[bars[i] - 1] = 1
            sPoint[i] = (bars[i] - prev - 1)/res
            prev = bars[i]
        #TODO: check if .copy() needed
        points = np.vstack((points, sPoint))
        data = sPoint @ datas
        ret, aVol = npSharpeRatio(data)
        retPoints.append(ret)
        aVolPoints.append(aVol)
        if (ret/aVol > maxSharpe):
            maxSharpe = ret/aVol
            maxPoint = sPoint
        mSharpe = ret/aVol
        mPoint = sPoint
        print('Starting Point')
        print(sPoint)
        if not round(sum(sPoint), 2) == 1.0:
            print(round(sum(sPoint), 2))
            raise Exception('ERROR: INVALID POINT')

        #stochastic hillclimbing
        #count is number of iterations that max has stayed the same
        count = 0
        t = 0
        print(points.shape)
        point = points.shape[0] - 1
        print(points[point])
        while(count < len(stocks)):
            nPoint = points[point]
            switch = random.sample(range(0, len(stocks)), 2)
            while(nPoint[switch[1]] < 1/res):
                switch = random.sample(range(0, len(stocks)), 2)
            nPoint = points[point]
            nPoint[switch[0]] += 1/res
            nPoint[switch[1]] -= 1/res
            data = nPoint @ datas
            ret, aVol = npSharpeRatio(data)
            retPoints.append(ret)
            aVolPoints.append(aVol)
            points = np.vstack((points, nPoint))
            sharpe = ret/aVol

            count += 1
            if (sharpe > mSharpe):
                mSharpe = sharpe
                mPoint = nPoint
                count = 0

            #ret
            p = 1/(1 + np.exp(len(stocks)*(retPoints[point]/aVolPoints[point] - sharpe)/(t+1)))
            move = np.random.choice([True, False], 1, [p, 1-p])
            if move:
                point = t
            t += 1
        #max of this iteration
        print('MAX')
        print(mSharpe)
        print(mPoint)
        time.sleep(1)
        if (mSharpe > maxSharpe):
            maxSharpe = mSharpe
            maxPoint = mPoint

    #final max
    print('FINAL MAX SHARPE')
    print(maxSharpe)
    print(maxPoint)

    #points = pd.DataFrame(retPoints, aVolPoints, columns = ['ret', aVol])
    #path = 'Data/sample/' + 'tdSharpe.csv'
    #points.to_csv(path)
    
    plt.scatter(aVolPoints, retPoints)
    plt.show()

#print(sharpe('DE'))
#ndSharpe(stockScraper.SPY()[:100])


def ndSharpeRatio(stocks, datas, split = 10):
    if (len(stocks) != len(datas)):
        print('ERROR: stocks and datas do no match')
    #TODO
    n=1

def cMovingAvg(stock, date = np.datetime64('today'), days = 90):
    yfinanceInfo.daily(stock)
    path = 'Data/Historical/' + stock + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    return cMoving(data, date = date, days = days)
    
def cMoving(data, date = np.datetime64('today'), days = 90):
    i = data.index.get_loc(date)
    series = data.iloc[i - days:i]['Close']
    avg = series.sum()/(days)
    return avg

def movingAvg(stock, days = 90, plot = False):
    yfinanceInfo.daily(stock)
    path = 'Data/Historical/' + stock + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    return moving(data, days, plot)
    
def moving(data, days = 90, plot = False):
    data.insert(len(data.columns), 'Avg', np.nan)

    series = data.iloc[0:days]['Close']
    avg = series.sum()/days
    data['Avg'][days] = avg
    for i in range(days + 1, len(data.index)):
        avg -= data['Close'][i-days]/days
        avg += data['Close'][i]/days
        data['Avg'][i] = avg

    if plot:
        plot1 = plt.figure(1)
        data['Close'].plot()
        data.iloc[days - 1:]['Avg'].plot()
        plt.show()

    return data[days - 1:]['Avg']

def standardDeviation(stock, date = np.datetime64('today'), days = 90):
    yfinanceInfo.daily(stock)
    path = 'Data/Historical/' + stock + '.csv'
    data = pd.read_csv(path, index_col = 0, parse_dates = True)
    i = data.index.get_loc(date)
    series = data.iloc[i - days: i]['Close']
    return series.std()

#movingAvg('AMZN', plot = True, days = 16)

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


