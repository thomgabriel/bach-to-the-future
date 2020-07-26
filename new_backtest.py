import tools
from tqdm import tqdm
import logger
import statistics as st
import pandas as  pd
import numpy as np
import ta
import ccxt
from datetime import datetime
import talib as tb
from time import sleep
from client import FtxClient

ftx = FtxClient()
market_name = 'SXP-PERP'
resolution = 3600 # TimeFrame in seconds.
limit = 5000
start_time = datetime.fromisoformat('2020-05-01 00:00:00').timestamp()
end_time = datetime.now().timestamp()

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]

pbar = tqdm(total=len(ohlcv))
statistics_logger = logger.setup_db('statistics')

##### Parameters #####
init_margin = 1.0
margin = init_margin
margins = []

leverage = 1
profit = 0.20 # +0.5% from market price
stop = 0.8
taker_fee= 0.00075
maker_fee = -0.00025

entry_time = 0
leave_time = 0
position_time = []

stops_reached = []
targets_reached = []

long_target = 0
long_stop = 0
long_entry = 0
long_qtd = 0

short_target = 0
short_stop = 0
short_entry = 0
short_qtd = 0

##### State Machine #####

reached_stop = False
reached_target = False
in_long = False
in_short = False

#//Definitions
ma50 = ta.trend.SMAIndicator(ohlcv.Close,50).sma_indicator() 
ma20 = ta.trend.SMAIndicator(ohlcv.Close,20).sma_indicator() 

bb = ta.volatility.BollingerBands(ohlcv.Close,20)
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
signals=[]
for num in range(100,len(ohlcv)):
    
    actualPrice = ohlcv.Close.iloc[num]
    high = ohlcv.High.iloc[num]
    low = ohlcv.Low.iloc[num]
    timestamp = ohlcv.datetime.iloc[num]

    #Check Execution
    #in Long
    if in_long == True:
        if high >= long_target:
            margin = margin + ((long_qtd/long_entry) - (long_qtd/long_target)) - (long_qtd/long_target * maker_fee)

            margins.append('L_target,{}'.format(margin))
            reached_target = True
            in_long = False

        if low <= long_stop:
            margin = margin + ((long_qtd/long_entry) - (long_qtd/long_stop)) - (long_qtd/long_stop * taker_fee)

            margins.append('L_stop,{}'.format(margin))
            reached_stop = True
            in_long = False

    if in_short == True: 
        if low <= short_target:
            margin = margin + ((short_qtd/short_target) - (short_qtd/short_entry)) - (short_qtd/short_target * maker_fee)

            margins.append('S_target,{}'.format(margin))
            reached_target = True
            in_short = False

        if high >= short_stop:
            margin = margin + ((short_qtd/short_stop) - (short_qtd/short_entry)) - (short_qtd/short_stop * taker_fee) 

            margins.append('S_stop,{}'.format(margin))
            reached_stop = True
            in_short = False

    # If reached Stop Loss   
    if reached_stop:
        reached_stop = False
        stops_reached.append([timestamp, actualPrice])
        leave_time = num
        position_time.append(leave_time - entry_time)

    # If reached Profit Target
    if reached_target:
        reached_target = False
        targets_reached.append([timestamp, actualPrice])
        leave_time = num
        position_time.append(leave_time - entry_time)

    if (not in_long) and (not in_short):
        
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
        elif (linreg[num-1]-linreg[num])/linreg[num] < -0.0002:
            ma_steepness = 1
        else:
            ma_steepness = 0

        if macdz_hist[num] > 0:
            macdz_direction = 1
        else:
            macdz_direction = -1

        if ma50_near_BB >= 1  and macdz_direction >= 1 and price_near_BB >= 1 and ma_steepness >= 1: #BUY SIGNAL
            
            long_qtd = round(actualPrice * margin * leverage * 1) # In contracts, entry only with 80% of available margin
            long_entry = actualPrice
            long_target = tools.toNearest(actualPrice + actualPrice * profit)
            long_stop = tools.toNearest(actualPrice - actualPrice * stop)
            in_long = True
            entry_time = num
            margin = margin - (long_qtd/long_entry * maker_fee)
            signals.append('LONG = {}'.format(timestamp))

        if ma50_near_BB <= -1 and macdz_direction <= -1 and price_near_BB <= -1 and ma_steepness <= -1: #SELL SIGNAL
            
            short_qtd = round(actualPrice * margin * leverage * 1) # In contracts, entry only with 80% of available margin
            short_entry = actualPrice
            short_target = tools.toNearest(actualPrice - actualPrice * profit)
            short_stop = tools.toNearest(actualPrice + actualPrice * stop)
            in_short = True
            entry_time = num
            margin = margin - (short_qtd/short_entry * maker_fee)
            signals.append('SHORT = {}'.format(timestamp))

    pbar.update(1)
pbar.close()

statistics_logger.info('Margin: {}, Profit/loss: {}, Stops: {}, Targets: {}'.format(round(margin,5),round((margin/init_margin) * 100,2),len(stops_reached),len(targets_reached)))
statistics_logger.info('Stops: {}'.format(stops_reached))
statistics_logger.info('Targets: {}'.format(targets_reached))
statistics_logger.info('margins: {}'.format(margins))
statistics_logger.info('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
statistics_logger.info('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
statistics_logger.info('Signals: {}'.format(signals))
statistics_logger.info('(////////////////////////////////////////////////////////')

print('///////////////////////////////')
print('-------------------------------')
print('Start: {}'.format(ohlcv.datetime.iloc[100]))
print('End: {}'.format(ohlcv.datetime.iloc[-1]))
print('Final Margin: {}'.format(round(margin,5)))
print('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
print('Stops: {}'.format(len(stops_reached)))
print('Targets: {}'.format(len(targets_reached)))
print('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
print('Mean Position Time {} min'.format(round(st.mean(position_time),2)))
print('-------------------------------')
print('///////////////////////////////')