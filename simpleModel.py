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

    def __init__(self, stock, sBalance, mLen):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'simpleMeanReversion' + stock
        self.mLen = mLen

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = self.mLen)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - self.mLen : i]['Close']
            avg = series.sum()/self.mLen
        if (price > avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}

    def idealPortfolios(self, startDate = dt.datetime(2020, 5, 18),
                        endDate = dt.datetime(2021, 5, 18)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        
        s = data.index.get_loc(startDate)
        e = data.index.get_loc(endDate)
        series = data.iloc[s - 1 - self.mLen : s - 1]['Close']
        avg = series.sum()/self.mLen

        dates = data.index[s:e+1]
        ports = pd.Series(index = dates, dtype = np.dtype(dict))
        for i in range(s, e+1):
            price = data['Close'].iloc[i]

            self.assets = self.cash
            for st in self.portfolio:
                self.assets += self.portfolio[st][0]*price

            avg -= data['Close'].iloc[i - 1 - self.mLen]/self.mLen 
            avg += data['Close'].iloc[i - 1]/self.mLen
            if (price > avg):
                vol = 0
            else:
                vol = math.floor(self.assets/price)
            self.portfolio = {self.stock : (vol, price)}
            ports.iat[i-s] = self.portfolio
            stockAssets = vol*price 
            self.cash = self.assets - stockAssets
        return ports

class simpleMomentum(Model):

    def __init__(self, stock, sBalance, mLen):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'simpleMomentum' + stock
        self.mLen = mLen

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = self.mLen)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            i = data.index.get_loc(date)
            series = data.iloc[i - self.mLen : i]['Close']
            avg = series.sum()/self.mLen
        if (price < avg):
            return {self.stock : (0, price)}
        else:
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}

    def idealPortfolios(self, startDate = dt.datetime(2020, 5, 18),
                        endDate = dt.datetime(2021, 5, 18)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        
        s = data.index.get_loc(startDate)
        e = data.index.get_loc(endDate)
        series = data.iloc[s - 1 - self.mLen : s - 1]['Close']
        avg = series.sum()/self.mLen

        dates = data.index[s:e+1]
        ports = pd.Series(index = dates, dtype = np.dtype(dict))
        for i in range(s, e+1):
            price = data['Close'].iloc[i]

            self.assets = self.cash
            for st in self.portfolio:
                self.assets += self.portfolio[st][0]*price

            avg -= data['Close'].iloc[i - 1 - self.mLen]/self.mLen 
            avg += data['Close'].iloc[i - 1]/self.mLen
            if (price < avg):
                vol = 0
            else:
                vol = math.floor(self.assets/price)
            self.portfolio = {self.stock : (vol, price)}
            ports.iat[i-s] = self.portfolio
            stockAssets = vol*price 
            self.cash = self.assets - stockAssets
        return ports

class meanReversion2(Model):

    def __init__(self, stock, sBalance, mLen, sdLen, stds):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'meanReversion2' + stock
        self.mLen = mLen
        self.sdLen = sdLen
        self.stds = stds

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        if (current):
            price = collectData.price(self.stock)
            avg = collectData.cMovingAvg(self.stock, days = self.mLen)
            sd = collectData.standardDeviation(self.stock, days = self.sdLen)
        else:
            path = 'Data/Historical/' + self.stock + '.csv'
            data = pd.read_csv(path, index_col = 0, parse_dates = True)
            price = data['Close'][date]
            avg = collectData.cMovingAvg(self.stock, date = date, days = self.mLen)
            sd = collectData.standardDeviation(self.stock, date = date, days = self.sdLen)
        if (price - avg > self.stds*sd):
            return {self.stock : (0, price)}
        elif (avg - price > self.stds*sd):
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}
        else:
            if self.stock in self.portfolio.keys():
                return {self.stock : (self.portfolio[self.stock], price)}
            else:
                return {}

    def idealPortfolios(self, startDate = dt.datetime(2020, 5, 18),
                        endDate = dt.datetime(2021, 5, 18)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        
        s = data.index.get_loc(startDate)
        e = data.index.get_loc(endDate)
        series = data.iloc[s - 1 - self.mLen : s - 1]['Close']
        avg = series.sum()/self.mLen

        dates = data.index[s:e+1]
        ports = pd.Series(index = dates, dtype = np.dtype(dict))
        #TODO: If further optimization needed, optimize standard deviation to
        #use past values
        for i in range(s, e+1):
            price = data['Close'].iloc[i]

            self.assets = self.cash
            for st in self.portfolio:
                self.assets += self.portfolio[st][0]*price

            avg -= data['Close'].iloc[i - 1 - self.mLen]/self.mLen 
            avg += data['Close'].iloc[i - 1]/self.mLen

            sdSeries = data['Close'].iloc[i - self.sdLen: i]
            sd = sdSeries.std()
            if (price - avg > self.stds*sd):
                vol = 0
            elif (avg - price > self.stds*sd):
                vol = math.floor(self.assets/price)
            else:
                if self.stock in self.portfolio.keys():
                    vol = self.portfolio[self.stock][0]
                else:
                    vol = 0
            self.portfolio = {self.stock : (vol, price)}
            ports.iat[i-s] = self.portfolio
            stockAssets = vol*price 
            self.cash = self.assets - stockAssets
        return ports

class meanReversionMomentum(Model):

    def __init__(self, stock, sBalance, mLen, sdLen, stds):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'meanReversionMomentum' + stock
        self.mLen = mLen
        self.sdLen = sdLen
        self.stds = stds

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

    def idealPortfolios(self, startDate = dt.datetime(2020, 5, 18),
                        endDate = dt.datetime(2021, 5, 18)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        
        s = data.index.get_loc(startDate)
        e = data.index.get_loc(endDate)
        series = data.iloc[s - 1 - self.mLen : s - 1]['Close']
        avg = series.sum()/self.mLen

        dates = data.index[s:e+1]
        ports = pd.Series(index = dates, dtype = np.dtype(dict))
        #TODO: If further optimization needed, optimize standard deviation to
        #use past values
        pPrice = data['Close'].iloc[s - 1]
        for i in range(s, e+1):
            price = data['Close'].iloc[i]

            self.assets = self.cash
            for st in self.portfolio:
                self.assets += self.portfolio[st][0]*price

            avg -= data['Close'].iloc[i - 1 - self.mLen]/self.mLen 
            avg += data['Close'].iloc[i - 1]/self.mLen

            sdSeries = data['Close'].iloc[i - self.sdLen: i]
            sd = sdSeries.std()
            if (price - avg > self.stds*sd and pPrice > price):
                vol = 0
            elif (avg - price > self.stds*sd and pPrice < price):
                vol = math.floor(self.assets/price)
            else:
                if self.stock in self.portfolio.keys():
                    vol = self.portfolio[self.stock][0]
                else:
                    vol = 0
            self.portfolio = {self.stock : (vol, price)}
            ports.iat[i-s] = self.portfolio
            stockAssets = vol*price 
            self.cash = self.assets - stockAssets
            pPrice = price
        return ports

class goldenCross(Model):

    def __init__(self, stock, sBalance, mLen1, mLen2):
        super().__init__(sBalance)
        self.stock = stock
        self.name = 'goldenCross' + stock
        self.mLen1 = mLen1
        self.mLen2 = mLen2

    def idealPortfolio(self, current = True, date = dt.datetime(2002, 8, 19)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        price = data['Close'][date]
        i = data.index.get_loc(date)
        series1 = data.iloc[i - 50 : i]['Close']
        pSeries1 = data.iloc[i - 51: i - 1]['Close']
        series2 = data.iloc[i - 200: i]['Close']
        pSeries2 = data.iloc[i - 201: i - 1]['Close']
        avg1 = series1.sum()/50
        pAvg1 = pSeries1.sum()/50
        avg2 = series2.sum()/200
        pAvg2 = pSeries2.sum()/200
        #comparing slopes
        if (avg1 - pAvg1 < avg2 - pAvg2):
            return {self.stock : (0, price)}
        elif (avg1 > avg2):
            vol = math.floor(self.assets/price)
            return {self.stock : (vol, price)}
        else:
            if self.stock in self.portfolio.keys():
                return {self.stock : (self.portfolio[self.stock], price)}
            else:
                return {}

    def idealPortfolios(self, startDate = dt.datetime(2020, 5, 18),
                        endDate = dt.datetime(2021, 5, 18)):
        path = 'Data/Historical/' + self.stock + '.csv'
        data = pd.read_csv(path, index_col = 0, parse_dates = True)
        
        s = data.index.get_loc(startDate)
        e = data.index.get_loc(endDate)
        series1 = data.iloc[s - 1 - self.mLen1 : s - 1]['Close']
        avg1 = series1.sum()/self.mLen1
        pAvg1 = avg1
        series2 = data.iloc[s - 1 - self.mLen2 : s - 1]['Close']
        avg2 = series2.sum()/self.mLen2
        pAvg2 = avg2

        dates = data.index[s:e+1]
        ports = pd.Series(index = dates, dtype = np.dtype(dict))
        #TODO: If further optimization needed, optimize standard deviation to
        #use past values
        for i in range(s, e+1):
            price = data['Close'].iloc[i]

            self.assets = self.cash
            for st in self.portfolio:
                self.assets += self.portfolio[st][0]*price

            avg1 -= data['Close'].iloc[i - 1 - self.mLen1]/self.mLen1 
            avg1 += data['Close'].iloc[i - 1]/self.mLen1
            avg2 -= data['Close'].iloc[i - 1 - self.mLen2]/self.mLen2 
            avg2 += data['Close'].iloc[i - 1]/self.mLen2

            #comparing slopes
            if (avg1 - pAvg1 < avg2 - pAvg2):
                vol = 0
            elif (avg1 > avg2):
                vol = math.floor(self.assets/price)
            else:
                if self.stock in self.portfolio.keys():
                    vol = self.portfolio[self.stock][0]
                else:
                    vol = 0
            self.portfolio = {self.stock : (vol, price)}
            ports.iat[i-s] = self.portfolio
            stockAssets = vol*price 
            self.cash = self.assets - stockAssets
            pAvg1 = avg1
            pAvg2 = avg2
        return ports

def buySell(model, current = True, date = dt.datetime(2002, 8, 19)):
    model.assets = model.cash
    for s in model.portfolio:
        p = stockPrice(s, current, date)
        model.assets += model.portfolio[s]*p
    #TODO: Test if p can be subbed out for goal[s][1]

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

def buySells(model, startDate = dt.datetime(2020, 5, 18),
             endDate = dt.datetime(2021, 5, 18),):
    goals = model.idealPortfolios(startDate, endDate)
    buySells = pd.Series(index = goals.index, dtype = np.dtype(dict))
    #setting up "goal" (starting portfolio)
    goal = {}
    for st in model.portfolio:
        goal[st] = (0, 0)
    for d in goals.index:
        #previous goal which is current portfolio
        port = goal
        goal = goals[d]

        buySell = {}
        for s in goal:
            buySell[s] = ((goal[s][0] - port[s][0]), goal[s][1])

        buySells.at[d] = buySell

    return buySells

test = goldenCross('AAPL', 5000, 50, 200)
#data = test.idealPortfolios()
#data.to_csv('Data/GoldenCross' + test.stock + '.csv')
print(buySells(test))
print(test.assets)

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
