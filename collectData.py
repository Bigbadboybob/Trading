import requests
import yfinance as yf
import time
import yfinanceInfo
import os
import stockScraper
import pandas as pd

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

def sharpeRatio(stockName):
    #TODO: add start and end date fields and handle cases of dates out of bounds etc
    #make default of 1 year if start and end not provided
    stockScraper.daily(stockName)
    path = 'Data/Historical/' + stockName + '.csv'
    data = pd.read_csv(path, index_col=0, parse_dates=True)
    startDate = data.index[0]
    days = len(data.index)
    endDate = data.index[days - 1]
    years = days/365.25
    CAGR = (data.at[endDate, 'Close']/data.at[startDate, 'Close'])**(1/years) - 1
    print(CAGR)
    riskFree = 0.0163
    #TODO: after learning pandas add a column with daily return


sharpeRatio('GOOG')
#yahooArticle('https://finance.yahoo.com/u/yahoo-finance/watchlists/the-autonomous-car')
#yfinanceInfo.plot("TSLA", "Close")
#yahooArticles(articles)
#sp = stockScraper.SP500()
#for s in sp:
#    time.sleep(1)
#    stockScraper.daily(t)
#    yfinanceInfo.baseInfo(t)


#earnings-netIncome
#shares-sharesOutstanding
#EPS-trailingEPS


