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
import datetime

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

    def simpleBacktest(self, model, startDate =  datetime.datetime(2020, 5, 18),
                       endDate = datetime.datetime(2021, 5, 18), generateLogs = True):
        if generateLogs:
            lPath = 'Data/simulationLogs/' + model.name + 'BackTest.csv'
            cols = ['Stock', 'Buy Date', 'Sell Date','Days', 'Buy Price',
                    'Sell Price', 'Volume', 'Total Gain','Gain per Day']
            logs = pd.DataFrame(columns = cols)
            r = 0

        for stock in self.stocks:
            yfinanceInfo.daily(stock)
            path = 'Data/Historical/' + stock + '.csv'
            #TODO: False for now
            data = pd.read_csv(path, index_col=0, parse_dates = True)
            series = data.loc[startDate:endDate]['Close']

        buys = {}
        for c in series.index:
            buySell = model.buySell(current = False, date = str(c.date()))
            
            for s in buySell:
                self.portfolio[s] += buySell[s][0]
                self.cash -= buySell[s][0]*buySell[s][1]

                if generateLogs:
                    print('BUYSELL')
                    print(buySell)
                    if buySell[s][0] > 0:
                        buys[s] = (buySell[s][0], buySell[s][1], c)
                    elif buySell[s][0] < 0:
                        if buySell[s][0] != -buys[s][0]:
                            print('ERROR: Sell differs from buy. Inaccurate logging')
                        row = pd.Series(index = cols)
                        row['Stock'] = s
                        row['Buy Date'] = str(buys[s][2].date())
                        row['Sell Date'] = str(c.date())
                        delta = c - buys[s][2]
                        row['days'] = delta.days
                        row['Buy Price'] = buys[s][1]
                        row['Sell Price'] = buySell[s][1]
                        row['Volume'] = -buySell[s][0]
                        row['Total Gain'] = (buySell[s][1] - buys[s][1])/buys[s][1]
                        row['Gain per Day'] = row['Total Gain']/row['days']
                        logs.loc[r] = row
                        r += 1

            if generateLogs:
                logs.to_csv(lPath)

            self.assets = self.cash
            for s in self.portfolio:
                p = simpleModel.stockPrice(s, current = False, date = str(c.date()))
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
#    print('MOMENTUM')
#    print('portfolio: ' + str(test0.portfolio))
#    print('cash:' + str(test0.cash))
#    print('assets:' + str(test0.assets))
#    print('PERMABUY = ' + str(permaBuyTest(s, 5000)))
    time.sleep(10)
