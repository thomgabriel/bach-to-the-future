import bitmex
import datetime
from time import sleep
from tqdm import tqdm
import csv

# 3 months = 131400 minuts = 132 requests
pbar = tqdm(total=132)
close = []
high = []
low = []

exchange = bitmex.bitmex(test=False)
last90D_= datetime.datetime.now() - datetime.timedelta(days=90)

print('GETTING DATA...')
with open('data.csv', 'w') as file:
    writer = csv.writer(file)
    for x in range(132):

        startTime = last90D_ + datetime.timedelta(minutes= (x*1000))
        endTime = last90D_ + datetime.timedelta(minutes= ((1+x)*1000)) 
        _data = exchange.Trade.Trade_getBucketed(symbol='XBTUSD', reverse=True, binSize='1m', startTime=startTime,endTime=endTime, count=1000).result()[0]
        for x in _data:
            close.append(x['close'])
            high.append(x['high'])
            low.append(x['low'])


        sleep(1.5)
        pbar.update(1)
    pbar.close()
    writer.writerow(close)
    writer.writerow(high)
    writer.writerow(low)
print(len(close))

def get_data():
    return close,high,low