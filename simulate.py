import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import yfinanceInfo
import collectData
import json
import math
import copy
import simpleModel
import time
import datetime as dt
import os

def permaBuyTest(stock, sBalance, startDate = dt.datetime(2020, 5, 18), endDate = dt.datetime(2021, 5, 18)):
    price = simpleModel.stockPrice(stock, False, startDate)
    vol = math.floor(sBalance/price)
    cash = sBalance - vol*price
    final = vol*simpleModel.stockPrice(stock, False, endDate) + cash
    return final


class SimpleTest():

    def __init__(self, sBalance, stocks, model):
        self.sBalance = sBalance
        self.cash = sBalance
        self.assets = sBalance
        self.stocks = stocks
        self.model = model
        self.portfolio = {}
        for s in stocks:
            self.portfolio[s] = 0

    def appendStocks(stocks):
        self.stocks.union(stocks)

    def removeStocks(stocks):
        self.stocks.difference(stocks)

    def simpleBacktest(self, startDate =  dt.datetime(2020, 5, 18),
                       endDate = dt.datetime(2021, 5, 18), generateLogs = True):
        if generateLogs:
            lPath = 'Data/simulationLogs/' + self.model.name + 'BackTest.csv'
            cols = ['Date', 'Portfolio', 'Assets', 'Stock Assets']
            cols1 = ['Stock', 'Buy Date', 'Sell Date','Days', 'Buy Price',
                    'Sell Price', 'Volume', 'Return','Return per Day'] 
            cols2 = ['Total Return', 'Holding', 'Cap Used Return', 'Stock Increase']
            logs = pd.DataFrame(columns = cols)
            logs1 = pd.DataFrame(columns = cols1)
            logs2 = pd.DataFrame(columns = cols2)
            r = 0
            r1 = 0

        for stock in self.stocks:
            collectData.daily(stock)
            path = 'Data/Historical/' + stock + '.csv'
            #TODO: False for now
            data = pd.read_csv(path, index_col=0, parse_dates = True)
            series = data.loc[startDate:endDate]['Close']

        buys = {}
        for c in series.index:
            buySell = simpleModel.buySell(self.model, current = False, date = c)
            
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
                        row['Return'] = (buySell[s][1] - buys[s][1])/buys[s][1]
                        row['Return per Day'] = row['Return']/row['Days']
                        logs1.loc[r1] = row
                        r1 += 1

            self.assets = self.cash
            for s in self.portfolio:
                p = simpleModel.stockPrice(s, current = False, date = c)
                self.assets += self.portfolio[s]*p

            if generateLogs:
                row = pd.Series(index = cols)
                row['Date'] = str(c)
                row['Portfolio'] = str(self.portfolio)
                row['Assets'] = self.assets
                row['Stock Assets'] = self.assets - self.cash
                logs.loc[r] = row
                r += 1

        if generateLogs:
            row = pd.Series(index = cols2)
            period = (endDate - startDate).days
            row['Total Return'] = (self.assets-self.sBalance)/self.sBalance
            row['Holding'] = logs1['Days'].sum()/period
            row['Cap Used Return'] = row['Total Return']/row['Holding']
            logs2.loc[0] = row
            i = 0
            for s in self.stocks:
                endPrice = simpleModel.stockPrice(s, current = False, date = endDate)
                startPrice = simpleModel.stockPrice(s, current = False, date = startDate)
                increase = (endPrice - startPrice)/startPrice
                logs2['Stock Increase'][i] = s + ': ' + str(increase)
                i += 1

            logs = pd.concat([logs, logs1, logs2], axis = 1)
            logs.to_csv(lPath)

    def plot(self):
        lPath = 'Data/simulationLogs/' + self.model.name + 'BackTest.csv'
        if not os.path.exists(lPath):
            print('ERROR: No logs for ' + self.model.name)
            return False
        data = pd.read_csv(lPath, index_col = 1, parse_dates = True)
        assets = data['Assets']

        fig = plt.figure()
        plt.plot(assets.index, assets.values)
        plt.title(self.model.name)
        plt.xlabel('Date')
        plt.ylabel('Assets')
        plt.ylim([self.sBalance*0.8, self.sBalance*2])
        tReturn = 'Total Return = ' + str(data['Total Return'].iloc[0])
        holding = 'Holding = ' + str(data['Holding'].iloc[0])
        cUsed = 'Cap Used Return = ' + str(data['Cap Used Return'].iloc[0])
        sIncrease = ''
        i = 0
        while isinstance(data['Stock Increase'][i], str):
            sIncrease = sIncrease + ' ' + data['Stock Increase'][i]
            i += 1
        txt = tReturn + '\n' + holding + ' ' + cUsed + '\n' + sIncrease
        plt.annotate(text = txt, xy = (data.index[0], self.sBalance*1.8))
        return fig

def categoryComparison():
    #TODO
    print('TODO')

#PARAMETER COMPARISON
def runTest(stocks, m, balance):
    returns = pd.Series([])
    hReturns = pd.Series([])
    for s in stocks:
        model = m(s, balance)
        test = SimpleTest(balance, {s}, model)
        #Comment here to skip test:
        #test.simpleBacktest()

        print('DONE')
        print('-----')
        print(test.model.name.upper())
        print('portfolio: ' + str(test.portfolio))
        print('cash:' + str(test.cash))
        print('assets:' + str(test.assets))
        print('PERMABUY = ' + str(permaBuyTest(s, balance)))

        f = test.plot()
        #f.savefig('Data/figures/' + test.model.name + '.png')
        plt.show()

        lPath = 'Data/simulationLogs/' + model.name + 'BackTest.csv'
        data = pd.read_csv(lPath, index_col = 1, parse_dates = True)
        r = data['Total Return'].iloc[0]
        h = data['Cap Used Return'].iloc[0]
        returns[returns.size] = r
        hReturns[hReturns.size] = h

    print(returns)
    print(hReturns)
    rAvg = returns.sum()/returns.size
    rStd = returns.std()
    hAvg = hReturns.sum()/hReturns.size
    hStd = hReturns.std()
    return (rAvg, hAvg, rStd, hStd)

test = ['MSFT', 'GOOG', 'AAPL']
model = simpleModel.simpleMeanReversion
balance = 5000
mLengths = [i for i in range(5, 10)]
mLengths += [2i for i in range(6, 20)]
mLengths += [5i for i in range(9, 30)]
#sLenghts = mLengths
for i in mLengths:
    print(runTest(test, model, balance, mLen))
time.sleep(1000)

def runTests(stocks, models, balance):
    for s in stocks:
        tests = []
        for m in models:
            t = SimpleTest(balance, {s}, m(s, balance))
            #Comment here to skip test:
            t.simpleBacktest()
            tests.append(t)

        print('DONE')
        print('-----')
        for t in tests:
            print(t.model.name.upper())
            print('portfolio: ' + str(t.portfolio))
            print('cash:' + str(t.cash))
            print('assets:' + str(t.assets))
        print('PERMABUY = ' + str(permaBuyTest(s, balance)))

        for t in tests:
            f = t.plot()
            f.savefig('Data/figures/' + t.model.name + '.png')
        plt.show()

test = ['MSFT', 'AAPL', 'GOOG', 'NIO', 'ACB', 'CGC', 'WTRG', 'TSLA', 'USDT-USD', 
        'ETH-USD', 'BNB-USD', 'ADA-USD']
test = ['MSFT']
balance = 5000
mean = simpleModel.simpleMeanReversion
momentum = simpleModel.simpleMomentum
mean2 = simpleModel.meanReversion2
meanMomentum = simpleModel.meanReversionMomentum
models = [mean, momentum, mean2, meanMomentum]

runTests(test, models, balance)
