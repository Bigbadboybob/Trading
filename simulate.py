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

    def plot(self, model):
        lPath = 'Data/simulationLogs/' + model.name + 'BackTest.csv'
        if not os.path.exists(lPath):
            print('ERROR: No logs for ' + model.name)
            return False
        data = pd.read_csv(lPath, index_col = 1, parse_dates = True)
        assets = data['Assets']
        sAssets = data['Stock Assets']

        invested = 1000*sAssets/assets 
        invested.round()
        invested = invested.astype(int)
        fig = plt.figure()

        plt.plot(assets.index, assets.values)
        plt.title(model.name)
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


test = ['MSFT', 'AAPL', 'GOOG', 'NIO', 'ACB', 'CGC', 'WTRG', 'TSLA', 'USDT-USD', 
        'ETH-USD', 'BNB-USD', 'ADA-USD']
balance = 5000
for s in test:
    mean = simpleModel.simpleMeanReversion(s, 5000)
    momentum = simpleModel.simpleMomentum(s, 5000)
    mean2 = simpleModel.meanReversion2(s, 5000)
    meanMomentum = simpleModel.meanReversionMomentum(s, 5000)

    test0 = SimpleTest(5000, {s})
    #test0.simpleBacktest(mean)

    test1 = SimpleTest(5000, {s})
    #test1.simpleBacktest(momentum)

    test2 = SimpleTest(5000, {s})
    #test2.simpleBacktest(mean2)

    test3 = SimpleTest(5000, {s})
    #test3.simpleBacktest(meanMomentum)

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

    fig0 = test0.plot(mean)
    fig1 = test1.plot(momentum)
    fig2 = test2.plot(mean2)
    fig3 = test3.plot(meanMomentum)
    plt.show()
