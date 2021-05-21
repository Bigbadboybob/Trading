import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinanceInfo
import collectData
import json
import math
import copy
import simpleModel
import time

def permaBuyTest(stock, sBalance, startDate = '2020-05-18', endDate = '2021-05-18'):
    price = simpleModel.stockPrice(stock, False, startDate)
    vol = math.floor(sBalance/price)
    cash = sBalance - vol*price
    final = vol*simpleModel.stockPrice(stock, False, endDate) + cash
    return final


class SimpleTest():

    def __init__(self, sBalance, stocks):
        self.cash = sBalance
        self.assets = sBalance
        self.stocks = stocks
        self.portfolio = {}
        for s in stocks:
            self.portfolio[s] = 0

    def appendStocks(stocks):
        self.stocks.union(stocks)

    def removeStocks(stocks):
        self.stocks.difference(stocks)

    def simpleBacktest(self, model, startDate =  '2020-05-18', endDate = '2021-05-18'):
        for stock in self.stocks:
            yfinanceInfo.daily(stock)
            path = 'Data/Historical/' + stock + '.csv'
            #TODO: False for now
            data = pd.read_csv(path, index_col=0, parse_dates=False)
            series = data.loc[startDate:endDate]['Close']
        for c in series.index:
            buySell = model.buySell(current = False, date = str(c))
            for s in buySell:
                self.portfolio[s] += buySell[s][0]
                self.cash -= buySell[s][0]*buySell[s][1]

            self.assets = self.cash
            for s in self.portfolio:
                p = simpleModel.stockPrice(s, current = False, date = str(c))
                self.assets += self.portfolio[s]*p

test = ['MSFT']
balance = 5000
for s in test:
    mean = simpleModel.simpleMeanReversion(s, 5000)
    momentum = simpleModel.simpleMomentum(s, 5000)

    test0 = SimpleTest(5000, {s})
    test0.simpleBacktest(mean)

    test1 = SimpleTest(5000, {s})
    test1.simpleBacktest(mean)
    print('DONE')
    print('-----')
    print('MEAN REVERSION')
    print('portfolio: ' + str(test0.portfolio))
    print('cash:' + str(test0.cash))
    print('assets:' + str(test0.assets))
    print('MOMENTUM')
    print('portfolio: ' + str(test0.portfolio))
    print('cash:' + str(test0.cash))
    print('assets:' + str(test0.assets))
    print('PERMABUY = ' + str(permaBuyTest(s, 5000)))
    time.sleep(10)
