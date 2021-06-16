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
import stockScraper
import time
import datetime as dt
import os
import random
from perlin_noise import PerlinNoise

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

        for stock in self.stocks:
            collectData.daily(stock)
            path = 'Data/Historical/' + stock + '.csv'
            data = pd.read_csv(path, index_col=0, parse_dates = True)
            series = data['Close'][startDate:endDate]

        buySells = simpleModel.buySells(self.model, startDate, endDate)
        vol = 0
        holding = 0
        for c in series.index:
            buySell = buySells[c]
            for s in buySell:
                vol += buySell[s][0]
            if vol > 0:
                holding += 1
        holding /= buySells.size

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

            buys = {}
            for c in series.index:
                #buySell = simpleModel.buySell(self.model, current = False, date = c)
                buySell = buySells[c]
                
                for s in buySell:
                    self.portfolio[s] += buySell[s][0]
                    self.cash -= buySell[s][0]*buySell[s][1]

                    if (buySell[s][0] > 0 and
                    #make sure we're not logging small rebuys
                    buySell[s][0]*[buySell[s][1] > self.assets/2]):
                        buys[s] = (buySell[s][0], buySell[s][1], c)
                    elif buySell[s][0] < 0:
                        if buySell[s][0] != -buys[s][0]:
                            print('ERROR: Sell differs from buy. Inaccurate logging')
                            time.sleep(60)
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

                row = pd.Series(index = cols)
                row['Date'] = str(c)
                row['Portfolio'] = str(self.portfolio)
                row['Assets'] = self.assets
                row['Stock Assets'] = self.assets - self.cash
                logs.loc[r] = row
                r += 1

            row = pd.Series(index = cols2)
            period = (endDate - startDate).days
            row['Total Return'] = (self.assets-self.sBalance)/self.sBalance
            row['Holding'] = holding
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

        returns = (self.model.assets - self.sBalance)/self.sBalance
        return returns, holding

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
def runTest(stocks, m, balance, params):
    returns = pd.Series([])
    hReturns = pd.Series([])
    for s in stocks:
        model = m(s, balance, params[0], params[1], params[2])
        test = SimpleTest(balance, {s}, model)
        #Comment here to skip test:
        r, h = test.simpleBacktest(startDate = dt.datetime(2020, 5, 18), 
                                   endDate = dt.datetime(2021, 5, 18), generateLogs = False)

        #print('DONE')
        #print('-----')
        #print(test.model.name.upper())
        #print('assets:' + str((r+1)*balance))
        #print('holding:' + str(h))
        #print('PERMABUY = ' + str(permaBuyTest(s, balance)))

        #f = test.plot()
        #f.savefig('Data/figures/' + test.model.name + '.png')
        #plt.show()

        #lPath = 'Data/simulationLogs/' + model.name + 'BackTest.csv'
        #data = pd.read_csv(lPath, index_col = 1, parse_dates = True)
        #r0 = data['Total Return'].iloc[0]
        #print(r0)
        #h0 = data['Cap Used Return'].iloc[0]
        #print(h0)
        returns[returns.size] = r
        if h != 0:
            hReturns[hReturns.size] = r/h

    rAvg = returns.sum()/returns.size
    rStd = returns.std()
    hAvg = hReturns.sum()/hReturns.size
    hStd = hReturns.std()
    print('TEST DONE')
    print('rAVG')
    print(rAvg)
    print('hAVG')
    print(hAvg)
    if np.isnan(hAvg):
        hAvg = 0.0
    return (rAvg, hAvg, rStd, hStd)

#test = ['MSFT']
#model = simpleModel.simpleMeanReversion
#balance = 5000
#stats = runTest(test, model, balance, 30)
#print(stats)
#time.sleep(100)

test = stockScraper.SPY()[:100]
#test.remove('OGN')
print(test)
model = simpleModel.meanReversionMomentum
balance = 5000
mLengths = [i for i in range(5, 10)]
mLengths += [2*i for i in range(5, 20)]
mLengths += [5*i for i in range(8, 41)]
sLengths = mLengths
stds = [i/20 for i in range(5, 60)]

#runTest(test, model, 5000, [mLengths[36], sLengths[32], stds[33]])
#time.sleep(1000)

#TODO: Figure out how to skip iterations using stochastic hillclimbing
#Perhaps time to take on the n-d sharpe ration problem
#optimize standard deviation calculation


#test this
def testFunc(c):
    m = c[0]
    s = c[1]
    sd = c[2]
    f = 3 - ( ((c[0]-17)/55)**2 + ((c[1]-30)/55)**2 + ((c[2]-6)/53)**2 )
    g = 6 - ( (2*(c[0]-10)/55)**2 + ((c[1]-24)/55)**2 + ((c[2]-50)/53)**2 )
    noise = PerlinNoise(octaves=3, seed=1)
    n = noise([c[0]/55, c[1]/55, c[2]/53])
    return (f + n, g + n)
#print(testFunc([31, 28, 16]))


#3.449
#31, 28, 16
#6.369
#15, 23, 33


#input is list of lists, each list corresponding to a single parameter and
#containing the values the will be tested for each parameter
def paramOptimization(params):
    def inBounds(point):
        for i in range(0, len(point)):
            p = point[i]
            if p < 0 or p > (len(params[i]) - 1):
                return False
        return True

    def put(array, indices, value):
        i = indices[0]
        if len(indices) == 1:
            np.put(array, i, value)
        else:
            np.put(array, i, put(array[i], indices[1:], value))
        return array

    dimensions = [len(p) for p in params]
    returns = np.empty(tuple(dimensions))
    returns[:] = np.nan
    hReturns = np.empty(tuple(dimensions))
    hReturns[:] = np.nan

    maxReturns = []
    maxPoints = {}
    maxhReturns = []
    maxhPoints = {}
    maxReturn = 0
    runtime = 0
    #Temporary
    params[2] = [i/20 for i in range(5, 20)]
    for i in range(0, 12):
        if i < 10:
            point = [random.randint(0, len(p)-1) for p in params]
            maxCount = 2
        elif i == 10:
            point = maxPoints[maxReturns[0]]
            maxCount = 30
        else:
            point = maxPoints[maxReturns[2]]
            maxCount = 30
        print('Starting Point')
        print(point)
        parameters = [params[p][point[p]] for p in range(0, len(point))]
        print('RUNNING TEST: ' + str(parameters) )
        stats = runTest(test, model, balance, parameters)
        prevR = stats[0]
        put(returns, point, prevR)
        put(hReturns, point, stats[1])
        #stochastic hillclimbing
        #count is number of iterations that max has stayed the same
        count = 0
        stuck = 0
        t = 10
        #TODO figure out *5
        mReturn = 0
        while(count < maxCount):
        #for t in range(0, 50, 1):
            chIndex = random.randint(0, len(params) - 1)
            posNeg = bool(random.getrandbits(1))
            nPoint = point.copy()
            if posNeg:
                nPoint[chIndex] += 1
            else:
                nPoint[chIndex] -= 1
            #Getting stuck not finding point
            while(not inBounds(nPoint)):
                nPoint = point.copy()
                chIndex = random.randint(0, len(params) - 1)
                posNeg = bool(random.getrandbits(1))
                if posNeg:
                    nPoint[chIndex] += 1
                else:
                    nPoint[chIndex] -= 1
                
            r = returns
            for n in nPoint:
                r = r[n]
            if np.isnan(r):
                runtime += 1
                parameters = [params[p][nPoint[p]] for p in range(0, len(nPoint))]
                print('RUNNING TEST: ' + str(parameters) )
                stats = runTest(test, model, balance, parameters)
                #stats = testFunc(nPoint)
                returns = put(returns, nPoint, stats[0])
                r = stats[0]
                hReturns = put(hReturns, nPoint, stats[1])
                h = stats[1]
            if r > mReturn:
                mReturn = r
                mPoint = nPoint.copy()
                count = 0

            #TODO: ret
            p = 1/(1 + np.exp(1000*(prevR - r)/(t+1)))
            print(p)
            move = np.random.choice([True, False], size = 1, p = [p, 1-p])
            print(move)
            if t > 1:
                t -= 1
            if stuck == 5:
                count += 1
                stuck = 0
            if move:
                point = nPoint.copy()
                prevR = r
                count += 1
                stuck = 0
        #max of this iteration
        print('MAX ITER')
        print(mReturn)
        print(mPoint)
        maxReturns.append(mReturn)
        #slightly inefficient
        maxReturns.sort(reverse = True)
        maxPoints[mReturn] = mPoint.copy()

    #final max
    print('FINAL MAX Return')
    print(maxReturns[0])
    print(maxPoints[maxReturns[0]])
    print('ALL MAX POINTS')
    print('--------------')
    print(maxPoints)
    time.sleep(120)

    runtime = 0
    params[2] = [i/20 for i in range(5, 60)]
    for i in range(0, 12):
        if i < 10:
            point = [random.randint(0, len(p)-1) for p in params]
            maxCount = 2
        elif i == 10:
            point = maxhPoints[maxhReturns[0]]
            maxCount = 30
        else:
            point = maxhPoints[maxhReturns[2]]
            maxCount = 30
        print('Starting Point')
        print(point)
        parameters = [params[p][point[p]] for p in range(0, len(point))]
        print('RUNNING TEST: ' + str(parameters) )
        stats = runTest(test, model, balance, parameters)
        prevhR = stats[1]
        put(hReturns, point, prevhR)
        #stochastic hillclimbing
        #count is number of iterations that max has stayed the same
        count = 0
        stuck = 0
        t = 10
        #TODO figure out *5
        mhReturn = 0
        while(count < maxCount):
        #for t in range(0, 50, 1):
            chIndex = random.randint(0, len(params) - 1)
            posNeg = bool(random.getrandbits(1))
            nPoint = point.copy()
            if posNeg:
                nPoint[chIndex] += 1
            else:
                nPoint[chIndex] -= 1
            while(not inBounds(nPoint)):
                nPoint = point.copy()
                chIndex = random.randint(0, len(params) - 1)
                posNeg = bool(random.getrandbits(1))
                if posNeg:
                    nPoint[chIndex] += 1
                else:
                    nPoint[chIndex] -= 1
                
            h = hReturns
            for n in nPoint:
                h = h[n]
            if np.isnan(h):
                runtime += 1
                parameters = [params[p][nPoint[p]] for p in range(0, len(nPoint))]
                print('RUNNING TEST: ' + str(parameters) )
                stats = runTest(test, model, balance, parameters)
                returns = put(returns, nPoint, stats[0])
                r = stats[0]
                hReturns = put(hReturns, nPoint, stats[1])
                h = stats[1]
            if h > mhReturn:
                mhReturn = h
                mhPoint = nPoint.copy()
                count = 0

            p = 1/(1 + np.exp(1000*(prevhR - h)/(t+1)))
            print(p)
            move = np.random.choice([True, False], size = 1, p = [p, 1-p])
            print(move)
            stuck += 1
            if stuck == 5:
                count += 1
                stuck = 0
            if t > 1:
                t -= 1
            if move:
                point = nPoint.copy()
                prevhR = h
                count += 1
                stuck = 0
        #max of this iteration
        print('MAX ITER')
        print(mhReturn)
        print(mhPoint)
        maxhReturns.append(mhReturn)
        #slightly inefficient
        maxhReturns.sort(reverse = True)
        maxhPoints[mhReturn] = mhPoint.copy()

    #final max
    print('FINAL MAX Return')
    print(maxhReturns[0])
    print(maxhPoints[maxhReturns[0]])
    print('ALL MAX POINTS')
    print('--------------')
    print(maxPoints)
    print(maxhPoints)

t1 = time.time()
paramOptimization([mLengths, sLengths, stds, ])
t2 = time.time()
print('TIME')
print(t2-t1)
time.sleep(3600)
#points = pd.DataFrame(retPoints, aVolPoints, columns = ['ret', aVol])
#path = 'Data/sample/' + 'tdSharpe.csv'
#points.to_csv(path)

for i in range(0, 20):
    coords = (random.randint(0, len(mLengths)-1), random.randint(0, len(sLengths)-1),
             random.randint(0, len(stds)-1))
    print('Starting Coords')
    print(coords)
    hCoords = (random.randint(0, len(mLengths)-1), random.randint(0, len(sLengths)-1),
             random.randint(0, len(stds)-1))
    maxReturn = 0
    current = 0
    while(maxReturn == current):
        #start at bottom corner of cube and check everything in cube
        #This will automatically skip the middle since the middle is already filled out
        check = (coords[0] - 1, coords[1] - 1, coords[2] - 1)
        current = -100000
        print('loop')
        for m in range(0, 3):
            for s in range(0, 3):
                for sd in range(0, 3):
                    c = (check[0] + m, check[1] + s, check[2] + sd)
                    if inBounds(c):
                        if np.isnan(returns[c[0]][c[1]][c[2]]):
                            #print('RUNNING TEST: ' + str(c[0]) +','+ str(c[1]) +','+ str(c[2]))
                            #stats = runTest(test, model, balance, mLengths[c[0]],
                            #                sLengths[c[1]], stds[c[2]])
                            stats = testFunc(c)
                            returns[c[0]][c[1]][c[2]] = stats[0]
                            hReturns[c[0]][c[1]][c[2]] = stats[1]
                        if returns[c[0]][c[1]][c[2]] > maxReturn:
                            maxReturn = returns[c[0]][c[1]][c[2]]
                            current = returns[c[0]][c[1]][c[2]]
                            coords = c
    maxhReturn = 0
    hCurrent = 0
    while(maxhReturn == hCurrent):
        #start at bottom corner of cube and check everything in cube
        #This will automatically skip the middle since the middle is already filled out
        hCheck = (hCoords[0] - 1, hCoords[1] - 1, hCoords[2] - 1)
        hCurrent = -100000
        print('hloop')
        for m in range(0, 3):
            for s in range(0, 3):
                for sd in range(0, 3):
                    hc = (hCheck[0] + m, hCheck[1] + s, hCheck[2] + sd)
                    #TODO: Allow algorithm to go through nan paths
                    if inBounds(hc):
                        if np.isnan(hReturns[hc[0]][hc[1]][hc[2]]):
                            #print('RUNNING TEST: ' + str(hc[0]) +','+ str(hc[1]) +','+ str(hc[2]))
                            #stats = runTest(test, model, balance, mLengths[hc[0]],
                            #                sLengths[hc[1]], stds[hc[2]])
                            #test function
                            #TODO: add noise and holding to function
                            stats = testFunc(hc)
                            returns[hc[0]][hc[1]][hc[2]] = stats[0]
                            hReturns[hc[0]][hc[1]][hc[2]] = stats[1]
                        if  hReturns[hc[0]][hc[1]][hc[2]] > maxhReturn:
                            maxhReturn = hReturns[hc[0]][hc[1]][hc[2]]
                            hCurrent = hReturns[hc[0]][hc[1]][hc[2]]
                            hCoords = hc
                        
    print('LOCAL MAX')
    print(coords)
    print(returns[coords[0]][coords[1]][coords[2]])
    print(maxReturn)
    print(hCoords)
    print(hReturns[hCoords[0]][hCoords[1]][hCoords[2]])
    print(maxhReturn)
    maxCoords.append(coords)
    maxReturns.append(maxReturn)
    maxhCoords.append(hCoords)
    maxhReturns.append(maxhReturn)
print(maxCoords)
print(maxReturns)
print(maxhCoords)
print(maxhReturns)
time.sleep(1000)

#TODO: plot points in 2d like sharpe ratio

returns = np.empty((0, len(sLengths), len(stds)))
hReturns = np.empty((0, len(sLengths), len(stds)))
maxReturn = -10
maxhReturn = -10
for m in mLengths:
    sReturns = np.empty((0, len(stds)))
    shReturns = np.empty((0, len(stds)))
    for s in sLengths:
        sdReturns = []
        sdhReturns = []
        for sd in stds:
            print('RUNNING TEST: ' + str(m) +','+ str(s) +','+ str(sd))
            #print('------------')
            #stats = runTest(test, model, balance, m, s, sd)
            #print(stats)
            stats = (m + s + sd, m*s*sd)
            if m == 20 and s == 10 and sd ==40:
                stats = (20000000000000, m*s*sd)
            if (stats[0] > maxReturn):
                maxReturn = stats[0]
                mReturn = (mLengths.index(m), sLengths.index(s), stds.index(sd))
            if (stats[1] > maxhReturn):
                maxhReturn = stats[1]
                mhReturn = (mLengths.index(m), sLengths.index(s), stds.index(sd))
            sdReturns.append(stats[0])
            sdhReturns.append(stats[1])
        sdr = np.array(sdReturns)
        sdhr = np.array(sdhReturns)

        sReturns = np.vstack((sReturns, sdr))
        shReturns = np.vstack((shReturns, sdhr))

    sReturns.shape = (1, len(sLengths), len(stds))
    shReturns.shape = (1, len(sLengths), len(stds))
    returns = np.vstack((returns, sReturns))
    hReturns = np.vstack((hReturns, shReturns))

print(returns[20][10][40])
print(returns[19][10][40])
print(returns[mReturn[0]][mReturn[1]][mReturn[2]])
mPlane = returns[mReturn[0]]
sPlane = returns[:,mReturn[1]]
sdPlane = returns[:,:,mReturn[2]]
print('PLANES')
print(mPlane.shape)
print(sPlane.shape)
print(sdPlane.shape)
plot1 = plt.figure(1)
plt.imshow(mPlane, cmap= 'hot', interpolation = 'nearest')
plot1 = plt.figure(2)
plt.imshow(sPlane, cmap= 'hot', interpolation = 'nearest')
plot1 = plt.figure(3)
plt.imshow(sdPlane, cmap= 'hot', interpolation = 'nearest')
plt.show()
print('done')

#fig, ax = plt.subplots()
#x = np.arange(len(mLengths))
#ax.bar(x + 0.00, returns, color = 'b', width = 0.35, label = 'Total Retuns')
#ax.bar(x + 0.35, hReturns, color = 'g', width = 0.35, label = 'Holding Period Returns')
#ax.set_xticks(x)
#font = {'family': 'serif',
#        'color':  'black',
#        'weight': 'normal',
#        'size': 8,
#        }
#ax.set_xticklabels([str(i) for i in mLengths], fontdict = font)
#ax.legend()
#ax.set_title('Parameter Comparison')
#fig.tight_layout()
#plt.show()
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
