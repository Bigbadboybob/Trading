import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinanceInfo
import collectData
import json
import math
import copy

class Model():

    def __init__(self, sBalance):
        self.cash = sBalance
        self.assets = sBalance
        self.portfolio = {}



class simpleMeanReversion(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock

    def idealPortfolio(self, current = True, date = '2002-08-19'):
        #TODO: decide whether or not to parse dates or use strings
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = False)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - 30 : i]['Close']
            avg = series.sum()/30
        if (price > avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}


    def buySell(self, current = True, date = '2002-08-19'):
        goal = self.idealPortfolio(current = current, date = date)
        buySell = {}
        keysP = self.portfolio.keys()
        for s in goal:
            if (s not in keysP):
                self.portfolio[s] = 0
            buySell[s] = ((goal[s][0] - self.portfolio[s]), goal[s][1])

        #We assume in the model the buy/sell orders do not fail
        for s in buySell:
            self.portfolio[s] += buySell[s][0]
            self.cash -= buySell[s][0]*buySell[s][1]

        self.assets = self.cash
        for s in self.portfolio:
            p = stockPrice(s, current, date)
            self.assets += self.portfolio[s]*p

        print('DAY PASSES')
        print('-----------')
        print(buySell)
        print('portfolio')
        print(self.portfolio)
        print('cash')
        print(self.cash)
        print('assets')
        print(self.assets)
        return buySell

class simpleMomentum(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock

    def idealPortfolio(self, current = True, date = '2002-08-19'):
        #TODO: decide whether or not to parse dates or use strings
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = False)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - 30 : i]['Close']
            avg = series.sum()/30
        if (price < avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}


    def buySell(self, current = True, date = '2002-08-19'):
        goal = self.idealPortfolio(current = current, date = date)
        buySell = {}
        keysP = self.portfolio.keys()
        for s in goal:
            if (s not in keysP):
                self.portfolio[s] = 0
            buySell[s] = ((goal[s][0] - self.portfolio[s]), goal[s][1])

        #We assume in the model the buy/sell orders do not fail
        for s in buySell:
            self.portfolio[s] += buySell[s][0]
            self.cash -= buySell[s][0]*buySell[s][1]

        self.assets = self.cash
        for s in self.portfolio:
            p = stockPrice(s, current, date)
            self.assets += self.portfolio[s]*p

        print('DAY PASSES')
        print('-----------')
        print(buySell)
        print('portfolio')
        print(self.portfolio)
        print('cash')
        print(self.cash)
        print('assets')
        print(self.assets)
        return buySell

def stockPrice(stock, current = True, date = '2020-05-18'):
    if (current):
        price = collectData.price(stock)
        avg = collectData.cMovingAvg(stock, days = 30)
    else:
        path = 'Data/Historical/' + stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = False)
        price = data['Close'][date]
        data = pd.read_csv(path, index_col = 0, parse_dates = False)
        price = data['Close'][date]
    return price
