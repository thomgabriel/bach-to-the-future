import bitmex
import datetime
from time import sleep
from tqdm import tqdm 
import json

jsons = []

DAYS = 90
days_in_minutes = round(days * 1440)
pbar = tqdm(total=round(days * 1440/1000)+1)

# candles = dict(candles = [])
exchange = bitmex.bitmex(test=False)
startTime = datetime.datetime.now()

print('GETTING DATA...')

def compile_candles():
    for x in range(round(days * 1440/1000)+1):
        
        endTime = startTime
        startTime = startTime - datetime.timedelta(minutes= (1000))

        data = exchange.Trade.Trade_getBucketed(symbol='XBTUSD', reverse=True, binSize='1m', startTime=startTime,endTime=endTime, count=1000).result()[0]

        for num in data:
            
            candles = dict(
            close = num['close'],
            high = num['high'],
            low = num['low'],
            timestamp = str(num['timestamp'])[:18])
            
            jsons.append(candles)
        
        sleep(1.2)
        pbar.update(1)
    pbar.close()

    with open('../../data/candles.json', 'w') as batman:
        json.dump(dict(candles=jsons[::-1]),batman)

if __name__ == "__main__":
    compile_candles()
