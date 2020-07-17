import csv
# import data
import func
import numpy as np
from matplotlib import pyplot as plt
import bitmex
from time import sleep
import ta
import pandas as pd

exchange = bitmex.bitmex(test=False)

def __ADX(candles,N=14):
    close,high,low = candles
    
    moveUP = np.zeros(len(high))
    PDM = moveUP
    
    moveDown = np.zeros(len(low))
    NDM = moveDown

    for i in range(1,len(close)):
        moveUP[i] = high[i] - high[i-1]
        moveDown[i] = low[i-1] - low[i]
        PDM[i] = moveUP[i] if moveUP[i]>0 else 0
        NDM[i] = moveDown[i] if moveDown[i]>0 else 0
    
    ATR = func.calc_med_ema((np.array(high)-np.array(low)),N)
    pDI = func.calc_med_ema(PDM,N) / ATR * 100
    nDI = func.calc_med_ema(NDM,N) / ATR * 100
    
    ADX = func.calc_med_ema(abs(pDI-nDI),N)/(pDI+nDI)* 100

    return (ADX,pDI,nDI)


while True:
    _data = exchange.Trade.Trade_getBucketed(symbol='XBTUSD' ,binSize='1m',reverse=True, count = 1000).result()[0][::-1]
    close = [x['close'] for x in _data]
    close = pd.DataFrame(close)

    high = [x['high'] for x in _data]
    high = pd.DataFrame(high)

    low = [x['low'] for x in _data]
    low = pd.DataFrame(low)

    candles = [[x['close'] for x in _data],[x['high'] for x in _data],[x['low'] for x in _data]]
    _ADX,pDI,nDI = __ADX(candles)
    print(_ADX[-1])
    print(nDI[-1])
    print(pDI[-1])
    print(candles[0][-1])
    print('///////////////////////////////////////')

    ADX = ta.trend.ADXIndicator(high= high[0], low= low[0], close= close[0], n= 14, fillna = True)

    print(ADX.adx()[999])
    print(ADX.adx_neg()[999])
    print(ADX.adx_pos()[999])
    # print(close[0])
    print('///////////////////////////////////////')
    print('///////////////////////////////////////')
    sleep(10)


ADX.adx().plot(label='ADX', color = 'black')
ADX.adx_neg().plot(label='DI -', color = 'red')
ADX.adx_pos().plot(label='DI +', color = 'green')
plt.show()

# plt.plot(ADX, color='black',label= 'ADX')
# plt.plot(pDI, color='green',label= 'pDI')
# plt.plot(nDI, color='red',label= 'nDI')
# plt.legend()
# plt.show()
