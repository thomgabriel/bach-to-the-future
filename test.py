import pandas as  pd
import numpy as np
import ta
import ccxt
import matplotlib.pyplot as plt
import datetime
import scipy.stats as sp
import talib as tb
# import sklearn
from time import sleep
from client import FtxClient
import dateparser

ftx = FtxClient()

market_name = 'BTC-PERP'
resolution = 900 # TimeFrame in seconds.
limit = 5000
start_time = datetime.datetime.fromisoformat('2020-07-15 00:00:00').timestamp()
end_time = datetime.datetime.now().timestamp()

data = ftx.get_historical_data(market_name,resolution,limit,start_time,end_time)

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]
ohlcv.datetime = ohlcv.datetime.apply(lambda x: dateparser.parse(x))

print(ohlcv.datetime.iloc[-1])
# symbol= 'BTC-PERP'
# timeframe= '15m'
# since= '2020-07-15T00:00:00Z'

# exchange = ccxt.ftx()
# ohlcv = pd.DataFrame(data=exchange.fetch_ohlcv(symbol, timeframe,exchange.parse8601 (since)))
# ohlcv.columns = ["datetime", "Open", "High", "Low", "Close", "Volume"]
# ohlcv.datetime = ohlcv.datetime.apply(lambda x: datetime.fromtimestamp(x / 1000))

#//Definitions
ma50 = ta.trend.SMAIndicator(ohlcv.Close,50).sma_indicator() 
ma20 = ta.trend.SMAIndicator(ohlcv.Close,20).sma_indicator() 

bb = ta.volatility.BollingerBands(close= ohlcv.Close,n = 20)
bb_top = bb.bollinger_hband()
bb_bottom = bb.bollinger_lband()

# //Fast
ema1= ta.trend.EMAIndicator(ohlcv.Close,12).ema_indicator()
ema2 = ta.trend.EMAIndicator(ema1,12).ema_indicator()
differenceFast = ema1 - ema2
zerolagEMA = ema1 + differenceFast
demaFast = (2 * ema1) - ema2
# //Slow
emas1= ta.trend.EMAIndicator(ohlcv.Close,26).ema_indicator()
emas2 = ta.trend.EMAIndicator(emas1,26).ema_indicator()
differenceSlow = emas1 - emas2
zerolagslowMA = emas1 + differenceSlow
demaSlow = (2 * emas1) - emas2
# //MACD LINE
ZeroLagMACD = demaFast - demaSlow
# //SIGNAL LINE
emasig1 = ta.trend.EMAIndicator(ZeroLagMACD,9).ema_indicator()
emasig2 = ta.trend.EMAIndicator(emasig1,9).ema_indicator()
signal = (2 * emasig1) - emasig2
macdz_hist = ZeroLagMACD -signal

linreg = tb.LINEARREG(ma50,10)


# print(len(ohlcv))
# print(linreg.iloc[-2])
# print(((linreg.iloc[-2]-linreg.iloc[-1])/linreg.iloc[-1]))
# plt.plot(linreg, color='green')
# plt.plot(ohlcv.Close, color='black')
# plt.show()

signals=[]
buy_signal = False
sell_signal = False

for num in range(100,len(ohlcv)):
    
   
# //Buy Sell Signal
    if ma50[num] > (ma20[num] + (bb_top[num] -ma20[num])/2):
        ma50_near_BB= -1
    elif ma50[num] < (ma20[num] - (ma20[num]-bb_bottom[num])/2):
        ma50_near_BB= 1
    else:
        ma50_near_BB= 0

    if ohlcv.High[num] > (ma20[num]+(bb_top[num] -ma20[num])/2):
        price_near_BB = -1
    elif ohlcv.Low[num] < (ma20[num]-(ma20[num]-bb_bottom[num])/2):
        price_near_BB = 1
    else:
        price_near_BB= 0

    if (linreg[num-1]-linreg[num])/linreg[num] > 0.0002:
        ma_steepness = -1
        # print('short = {}'.format((linreg[num-1]-linreg[num])/linreg[num]))
    elif (linreg[num-1]-linreg[num])/linreg[num] < -0.0002:
        ma_steepness = 1
        # print('long = {}'.format((linreg[num-1]-linreg[num])/linreg[num]))
    else:
        ma_steepness = 0

    if macdz_hist[num] > 0:
        macdz_direction = 1
    else:
        macdz_direction = -1

    if ma50_near_BB >= 1  and macdz_direction >= 1 and price_near_BB >= 1 and ma_steepness >= 1:
        buy_signal = True

    if ma50_near_BB <= -1  and macdz_direction <= -1 and price_near_BB <= -1 and ma_steepness <= -1:
        sell_signal = True

    if buy_signal:
        signals.append('LONG-{}'.format(ohlcv.datetime[num]))
        buy_signal = False

    if sell_signal:
        signals.append('SHORT-{}'.format(ohlcv.datetime[num]))
        sell_signal = False

for x,y in enumerate(signals):
    print(x,y)
print('///////////////////')
print('ma50: {}'.format(ma50.iloc[-1]))
print('ma20: {}'.format(ma20.iloc[-1]))
print('bbtop: {}'.format(bb_top.iloc[-1]))
print('bbbot: {}'.format(bb_bottom.iloc[-1]))
print('linereg -1: {}'.format(linreg.iloc[-2]))
print('linereg : {}'.format(linreg.iloc[-1]))
print('std : {}'.format(bb_top.iloc[-1]-ma20.iloc[-1]))
print('macd : {}'.format(macdz_hist.iloc[-1]))
print(ohlcv.datetime.iloc[-1])

# 0 LONG-2020-07-21T16:15:00+00:00
# 1 LONG-2020-07-21T16:30:00+00:00
# 2 LONG-2020-07-23T03:45:00+00:00
# 3 LONG-2020-07-23T04:00:00+00:00
# 4 LONG-2020-07-23T04:15:00+00:00
# 5 LONG-2020-07-23T05:00:00+00:00
# 6 LONG-2020-07-23T05:15:00+00:00
# 7 LONG-2020-07-23T05:30:00+00:00
# 8 LONG-2020-07-23T05:45:00+00:00
# 9 LONG-2020-07-23T08:00:00+00:00
# 10 LONG-2020-07-26T00:00:00+00:00
# 11 LONG-2020-07-26T00:15:00+00:00
