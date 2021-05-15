import requests
import yfinance as yf
import time
import yfinanceInfo

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
        yfinanceInfo.daily(t)
        yfinanceInfo.baseInfo(t)

def yahooArticles(urls):
    for u in urls:
        yahooArticle(u)

articles = ['https://finance.yahoo.com/u/yahoo-finance/watchlists/the-autonomous-car',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/video-game-stocks',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/420_stocks',
                 'https://finance.yahoo.com/u/yahoo-finance/watchlists/electronic-trading-stocks',
                 ]

yahooArticle('https://finance.yahoo.com/u/yahoo-finance/watchlists/the-autonomous-car')
yfinanceInfo.plot("TSLA", "Close")
#yahooArticles(articles)


#earnings-netIncome
#shares-sharesOutstanding
#EPS-trailingEPS


