import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import json


def daily(stockName):
    ticker = yf.Ticker(stockName)
    data = ticker.history(period="max")
    path = 'Data/Historical/' + stockName + '.csv'
    data.to_csv(path)

def baseInfo(stockName):
    ticker = yf.Ticker(stockName)
    data = ticker.info
    outfile = open("Data/Info/" + stockName + ".json", 'w')
    json.dump(data, outfile)

def plot(stockName, key):
    path = 'Data/Historical/' + stockName + '.csv'
    data = pd.read_csv(path)
    data[key].plot()
    plt.title(stockName)
    plt.show()

#daily('MSFT')
#daily('GOOG')
#plot('MSFT', 'Close')
#plot('GOOG', 'Close')
baseInfo('MSFT')

