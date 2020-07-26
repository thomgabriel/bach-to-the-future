import bitmex
import datetime
from time import sleep
from tqdm import tqdm
import csv

days = 90
days_in_minutes = round(days * 1440)
pbar = tqdm(total=round(days * 1440/1000)+1)

close = []
high = []
low = []
timeframe = []

exchange = bitmex.bitmex(test=False)
startTime = datetime.datetime.now()

print('GETTING DATA...')
with open('data.csv', 'w') as file:
    writer = csv.writer(file, delimiter = ',')

    for x in range(round(days * 1440/1000)+1):
        
        endTime = startTime
        startTime = startTime - datetime.timedelta(minutes= (1000))
    
        data = exchange.Trade.Trade_getBucketed(symbol='XBTUSD', reverse=True, binSize='1m', startTime=startTime,endTime=endTime, count=1000).result()[0]

        for num in data:
            close.append(num['close'])
            high.append(num['high'])
            low.append(num['low'])
            timeframe.append(str(num['timestamp'])[:18])

        sleep(1.5)
        pbar.update(1)
    pbar.close()

    writer.writerow(close[::-1])
    writer.writerow(high[::-1])
    writer.writerow(low[::-1])
    writer.writerow(timeframe[::-1])
