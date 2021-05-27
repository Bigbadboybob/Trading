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
import datetime as dt

def permaBuyTest(stock, sBalance, startDate = dt.datetime(2020, 5, 18), endDate = dt.datetime(2021, 5, 18)):
    price = simpleModel.stockPrice(stock, False, startDate)
    vol = math.floor(sBalance/price)
    cash = sBalance - vol*price
    final = vol*simpleModel.stockPrice(stock, False, endDate) + cash
    return final


class SimpleTest():

    def __init__(self, sBalance, stocks):
        self.sBalance = sBalance
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

    def simpleBacktest(self, model, startDate =  dt.datetime(2020, 5, 18),
                       endDate = dt.datetime(2021, 5, 18), generateLogs = True):
        if generateLogs:
            lPath = 'Data/simulationLogs/' + model.name + 'BackTest.csv'
            cols = ['Stock', 'Buy Date', 'Sell Date','Days', 'Buy Price',
                    'Sell Price', 'Volume', 'Total Return','Return per Day', 
                   'Holding', 'Cap Used Return', 'Stock Increase']
            logs = pd.DataFrame(columns = cols)
            r = 0

        for stock in self.stocks:
            collectData.daily(stock)
            path = 'Data/Historical/' + stock + '.csv'
            #TODO: False for now
            data = pd.read_csv(path, index_col=0, parse_dates = True)
            series = data.loc[startDate:endDate]['Close']

        buys = {}
        for c in series.index:
            buySell = simpleModel.buySell(model, current = False, date = c)
            
            for s in buySell:
                self.portfolio[s] += buySell[s][0]
                self.cash -= buySell[s][0]*buySell[s][1]

                if generateLogs:
                    if buySell[s][0] > 1:
                        buys[s] = (buySell[s][0], buySell[s][1], c)
                    elif buySell[s][0] < 0:
                        if buySell[s][0] != -buys[s][0]:
                            print('ERROR: Sell differs from buy. Inaccurate logging')
                        row = pd.Series(index = cols)
                        row['Stock'] = s
                        row['Buy Date'] = str(buys[s][2].date())
                        row['Sell Date'] = str(c.date())
                        delta = c - buys[s][2]
                        row['Days'] = delta.days
                        row['Buy Price'] = buys[s][1]
                        row['Sell Price'] = buySell[s][1]
                        row['Volume'] = -buySell[s][0]
                        row['Total Return'] = (buySell[s][1] - buys[s][1])/buys[s][1]
                        row['Return per Day'] = row['Total Return']/row['Days']
                        time.sleep(10)
                        logs.loc[r] = row
                        r += 1

        self.assets = self.cash
        for s in self.portfolio:
            p = simpleModel.stockPrice(s, current = False, date = str(c.date()))
            self.assets += self.portfolio[s]*p

        if generateLogs:
            row = pd.Series(index = cols)
            row['Total Return'] = 'Total Return'
            row['Holding'] = 'Holding'
            row['Cap Used Return'] = 'Cap Used Return'
            logs.loc[r] = row
            r += 1
            row = pd.Series(index = cols)
            period = (endDate - startDate).days
            row['Total Return'] = (self.assets-self.sBalance)/self.sBalance
            row['Holding'] = logs['Days'].sum()/period
            row['Cap Used Return'] = row['Total Return']/row['Holding']
            logs.loc[r] = row
            i = 0
            for s in self.stocks:
                endPrice = simpleModel.stockPrice(s, current = False, date = endDate)
                startPrice = simpleModel.stockPrice(s, current = False, date = startDate)
                increase = (endPrice - startPrice)/startPrice
                logs['Stock Increase'][i] = s + ': ' + str(increase)
                i += 1

            logs.to_csv(lPath)


test = ['MSFT', 'AAPL', 'GOOG', 'NIO', 'ACB', 'CGC', 'WTRG', 'TSLA', 'USDT-USD', 
        'ETH-USD', 'BNB-USD', 'ADA-USD']
balance = 5000
for s in test:
    mean = simpleModel.simpleMeanReversion(s, 5000)
    momentum = simpleModel.simpleMomentum(s, 5000)
    mean2 = simpleModel.meanReversion2(s, 5000)
    meanMomentum = simpleModel.meanReversionMomentum(s, 5000)

    test0 = SimpleTest(5000, {s})
    test0.simpleBacktest(mean)

    test1 = SimpleTest(5000, {s})
    test1.simpleBacktest(momentum)

    test2 = SimpleTest(5000, {s})
    test2.simpleBacktest(mean2)

    test3 = SimpleTest(5000, {s})
    test3.simpleBacktest(meanMomentum)

    print('DONE')
    print('-----')
    print('MEAN REVERSION')
    print('portfolio: ' + str(test0.portfolio))
    print('cash:' + str(test0.cash))
    print('assets:' + str(test0.assets))
    print('MOMENTUM')
    print('portfolio: ' + str(test1.portfolio))
    print('cash:' + str(test1.cash))
    print('assets:' + str(test1.assets))
    print('MEAN REVERSION 2')
    print('portfolio: ' + str(test2.portfolio))
    print('cash:' + str(test2.cash))
    print('assets:' + str(test2.assets))
    print('MEAN REVERSION MOMENTUM')
    print('portfolio: ' + str(test3.portfolio))
    print('cash:' + str(test3.cash))
    print('assets:' + str(test3.assets))
    print('PERMABUY = ' + str(permaBuyTest(s, 5000)))
