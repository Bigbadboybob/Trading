import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinanceInfo
import collectData
import json
import math
import copy
import datetime as dt
import time

class Model():

    def __init__(self, sBalance):
        self.cash = sBalance
        self.assets = sBalance
        self.portfolio = {}


class simpleMeanReversion(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'simpleMeanReversion' + stock

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - 30 : i]['Close']
            avg = series.sum()/30
        if date == dt.datetime(2020, 6, 26) or date == dt.datetime(2020, 11, 3):
            time.sleep(10)
        if (price > avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}


class simpleMomentum(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'simpleMomentum' + stock

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        #TODO: decide whether or not to parse dates or use strings
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - 30 : i]['Close']
            avg = series.sum()/30
        if (price < avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}

class meanReversion2(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'meanReversion2' + stock

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
            sd = collectData.standardDeviation(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            avg = collectData.cMovingAvg(self.stock, date = date, days = 30)
            sd = collectData.standardDeviation(self.stock, date = date, days = 30)
        if (price - avg > sd):
            return {self.stock : (0, price)}
        elif (avg - price > sd):
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}
        else:
            if self.stock in self.portfolio.keys():
                return {self.stock : (self.portfolio[self.stock], price)}
            else:
                return {}

class meanReversionMomentum(Model):

    def __init__(self, stock, sBalance):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'meanReversionMomentum' + stock

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = 30)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            pPrice = data.iloc[i - 1]['Close']
            series = data.iloc[i - 30 : i]['Close']
            avg = series.sum()/30
            sd = collectData.standardDeviation(self.stock, date = date, days = 30)
        if (price - avg > sd/2 and pPrice > price):
            return {self.stock : (0, price)}
        elif (avg - price > sd/2 and pPrice < price):
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}
        else:
            if self.stock in self.portfolio.keys():
                return {self.stock : (self.portfolio[self.stock], price)}
            else:
                return {}


def buySell(model, current = True, date = dt.datetime(2002, 8, 19)):
    model.assets = model.cash
    for s in model.portfolio:
        p = stockPrice(s, current, date)
        model.assets += model.portfolio[s]*p

    goal = model.idealPortfolio(current = current, date = date)
    buySell = {}
    keysP = model.portfolio.keys()
    for s in goal:
        if (s not in keysP):
            model.portfolio[s] = 0
        buySell[s] = ((goal[s][0] - model.portfolio[s]), goal[s][1])

    #We assume in the model the buy/sell orders do not fail
    for s in buySell:
        model.portfolio[s] += buySell[s][0]
        model.cash -= buySell[s][0]*buySell[s][1]

    #TODO: Consolidate
    model.assets = model.cash
    for s in model.portfolio:
        p = stockPrice(s, current, date)
        model.assets += model.portfolio[s]*p

    return buySell

def stockPrice(stock, current = True, date = dt.datetime(2020, 5, 18)):
    if (current):
        price = collectData.price(stock)
    else:
        path = 'Data/Historical/' + stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        price = data['Close'][date]
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        price = data['Close'][date]
    return price
