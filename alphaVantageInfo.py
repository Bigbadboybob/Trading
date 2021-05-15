import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import time
import matplotlib.pyplot as plt
import os, sys, stat

api_key = '0DCLKLE3ZEZITZHW'

ts = TimeSeries(key=api_key, output_format='pandas')
data, meta_data = ts.get_intraday(symbol='MSFT', interval = '1min', outputsize = 'full')
print(data)
print(type(data))

def daily(stockName):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_daily(symbol=stockName, outputsize = 'full')
    print(data)
    path = 'Data/' + stockName + '.csv'
    #TODO: Figure out permissions for csv
    #os.chmod(path, stat.S_IRWXO)
    data.to_csv(path)
    data['4. close'].plot()
    plt.title('daily price')
    plt.show()

daily('MSFT')


i = 1
#while i==1:
    #    data, meta_data = ts.get_intraday(symbol='MSFT', interval = '1min', outputsize = 'full')
    #    data.to_excel("output.xlsx")
    #    time.sleep(60)

    #close_data = data['4. close']
    #percentage_change = close_data.pct_change()

    #print(percentage_change)

    #last_change = percentage_change[-1]

    #if abs(last_change) > 0.0004:
            #print("MSFT Alert:" + str(last_change))
