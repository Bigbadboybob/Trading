import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import traceback
import datetime as dt


def daily(stockName):
    pathj = 'Data/calcStats/' + stockName + '.json'
    path = 'Data/Historical/'+ stockName + '.csv'
    if (os.path.exists(pathj) and os.path.getsize(pathj)>2):
        jsonFile = open(pathj, 'r')
        j = json .load(jsonFile)
        if (j.get('lastUpdate') == str(dt.date.today())):
            data = pd.read_csv(path, parse_dates = True)
            return data
        jsonFile = open(pathj, 'w')
    else:
        j = {}
        jsonFile = open(pathj, 'w')
    ticker = yf.Ticker(stockName)
    data = ticker.history(period="max")
    data.to_csv(path)
    try:
        today = data.tail(1).iloc[0]
    except Exception as e:
        return data
        jsonFile.close()
    try:
        j['price'] = today['Close']
        j['lastUpdate'] = str(dt.date.today())
        json.dump(j, jsonFile)
        jsonFile.close()
    except Exception as e:
        print(traceback.format_exc())
        jsonFile.close()
        jsonFile = open(pathj, 'w')
        json.dump({}, jsonFile)
        jsonFile.close()
    return data


def baseInfo(stockName):
    ticker = yf.Ticker(stockName)
    data = ticker.info
    outfile = open("Data/info/" + stockName + ".json", 'w')
    json.dump(data, outfile)

def plot(stockName, key):
    path = 'Data/Historical/' + stockName + '.csv'
    data = pd.read_csv(path)
    data[key].plot()
    plt.title(stockName)
    plt.show()



