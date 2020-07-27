from tqdm import tqdm
import pandas as  pd
import numpy as np
import ta
from time import sleep
from datetime import datetime
import talib as tb
import dateparser
import math

import backtest.util.tools as tools
import backtest.util.logger as logger
import backtest.util.settings as settings
from backtest.util.api_ftx import FtxClient

ftx = FtxClient()
market_name = 'BTC-PERP'
resolution = 900 # TimeFrame in seconds.
limit = 5000
start_time = datetime.fromisoformat('2020-05-01 00:00:00').timestamp()
end_time = datetime.now().timestamp()

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]
ohlcv.datetime = ohlcv.datetime.apply(lambda x: dateparser.parse(x[:18]))

pbar = tqdm(total=len(ohlcv))
_logger = logger.setup_logger()
statistics_logger = logger.setup_db('../../../data/statistics/statistics')

H1_ohlcv = ohlcv.iloc[::4]

##### Define Parameters #####
margin = settings.init_margin
leaves = []
signals=[]
stops_reached = []
targets_reached = []
short_signals = []
long_signals = []

entry_time = 0
leave_time = 0
position_time = []

state_long = 0
long_target = 0
long_stop = 0
long_entry = 0
long_qtd = 0

state_short = 0
short_target = 0
short_stop = 0
short_entry = 0
short_qtd = 0

##### State Machine #####
reached_stop = False
reached_target = False
in_long = False
in_short = False

RSI = ta.momentum.RSIIndicator(H1_ohlcv.Close, 14).rsi() 
# //SMA'S
ma50 = ta.trend.SMAIndicator(ohlcv.Close,50).sma_indicator() 
ma20 = ta.trend.SMAIndicator(ohlcv.Close,20).sma_indicator() 
# //BOLLINGER BANDS
bb = ta.volatility.BollingerBands(ohlcv.Close,20)
bb_top = bb.bollinger_hband()
bb_bottom = bb.bollinger_lband()
# //MACD'S Fast EMA 
ema1= ta.trend.EMAIndicator(ohlcv.Close,12).ema_indicator()
ema2 = ta.trend.EMAIndicator(ema1,12).ema_indicator()
differenceFast = ema1 - ema2
zerolagEMA = ema1 + differenceFast
demaFast = (2 * ema1) - ema2
# //MACD'S Slow EMA 
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
# //LINEAR REGRESSION
linreg = tb.LINEARREG(ma50,10)

for num in range(100,len(ohlcv)):
    
    actualPrice = ohlcv.Close.iloc[num]
    high = ohlcv.High.iloc[num]
    low = ohlcv.Low.iloc[num]
    timestamp = ohlcv.datetime.iloc[num]

    #Check Execution
    #in Long
    if in_long == True:
        print((RSI.iloc[math.floor(num/4)],timestamp))
        if RSI.iloc[math.floor(num/4)] >= 75:
            leaves.append('L_target,{}'.format(timestamp))
            reached_target = True
            in_long = False
            margin = margin + ((long_qtd/long_entry) - (long_qtd/actualPrice)) - (long_qtd/actualPrice * settings.maker_fee)

        if RSI.iloc[math.floor(num/4)] <= 35:
            leaves.append('L_stop, {}'.format(timestamp))
            reached_stop = True
            in_long = False
            margin = margin + ((long_qtd/long_entry) - (long_qtd/actualPrice)) - (long_qtd/actualPrice * settings.taker_fee)

        if low <= long_stop:
            margin = margin + ((long_qtd/long_entry) - (long_qtd/long_stop)) - (long_qtd/long_stop * settings.taker_fee)
            leaves.append('*L_stop, {}'.format(timestamp))
            reached_stop = True
            in_long = False

    if in_short == True:         
        if RSI.iloc[math.floor(num/4)] <= 20: 
            leaves.append('S_target, {}'.format(timestamp))
            reached_target = True
            in_short = False
            margin = margin + ((short_qtd/actualPrice) - (short_qtd/short_entry)) - (short_qtd/actualPrice * settings.maker_fee)

        if RSI.iloc[math.floor(num/4)] >= 60:
            leaves.append('S_stop, {}'.format(timestamp))
            reached_stop = True
            in_short = False
            margin = margin + ((short_qtd/actualPrice) - (short_qtd/short_entry)) - (short_qtd/actualPrice * settings.taker_fee) 

        if high >= short_stop:
            margin = margin + ((short_qtd/short_stop) - (short_qtd/short_entry)) - (short_qtd/short_stop * settings.taker_fee) 
            leaves.append('*S_stop, {}'.format(timestamp))
            reached_stop = True
            in_short = False

    # If reached Stop Loss   
    if reached_stop:
        reached_stop = False
        stops_reached.append((timestamp, actualPrice))
        leave_time = num
        position_time.append(leave_time - entry_time)

    # If reached Profit Target
    if reached_target:
        reached_target = False
        targets_reached.append((timestamp, actualPrice))
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
            state_long = 1
        if state_long == 1:
            if actualPrice <= bb_bottom[num]:
                state_long = 2 
                long_qtd = round(actualPrice * margin * settings.leverage * 1) # In contracts, entry only with 80% of available margin
                long_entry = actualPrice - 1
        if state_long == 2:
            if actualPrice <= long_entry:
                long_stop = tools.toNearest(actualPrice - ((actualPrice - bb_bottom[num])*2))
                in_long = True
                entry_time = num
                margin = margin - (long_qtd/long_entry * settings.maker_fee)
                signals.append('LONG = {}'.format(timestamp))
                long_signals.append((timestamp, actualPrice))
                state_long = 0

        if ma50_near_BB <= -1 and macdz_direction <= -1 and price_near_BB <= -1 and ma_steepness <= -1: #SELL SIGNAL
            state_short = 1
        if state_short == 1:
            if actualPrice >= bb_top[num]:
                state_short = 2
                short_qtd = round(actualPrice * margin * settings.leverage * 1) # In contracts, entry only with 80% of available margin
                short_entry = actualPrice + 1
        if state_short == 2:
            if actualPrice >= short_entry:
                short_stop = tools.toNearest(actualPrice + ((actualPrice - bb_bottom[num])*2))
                in_short = True
                entry_time = num
                margin = margin - (short_qtd/short_entry * settings.maker_fee)
                signals.append('SHORT = {}'.format(timestamp))
                short_signals.append((timestamp, actualPrice))
                state_short = 0
    pbar.update(1)
pbar.close()

statistics_logger.info('Final Margin: {}, Profit/loss: {}, Stops: {}, Targets: {}'.format(round(margin,5),round((margin/settings.init_margin) * 100,2),len(stops_reached),len(targets_reached)))
statistics_logger.info('Profit/loss: {}%'.format(round(((margin/settings.init_margin-1) * 100),2)))
statistics_logger.info('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
statistics_logger.info('Stops: {}'.format(stops_reached))
statistics_logger.info('Targets: {}'.format(targets_reached))
statistics_logger.info('Signals: {}'.format(signals))
statistics_logger.info('Leaves: {}'.format(leaves))
statistics_logger.info('\n \n \n')

_logger.info('///////////////////////////////')
_logger.info('-------------------------------')
_logger.info('Start: {}'.format(ohlcv.datetime.iloc[100]))
_logger.info('End: {}'.format(ohlcv.datetime.iloc[-1]))
_logger.info('Final Margin: {}'.format(round(margin,5)))
_logger.info('Profit/loss: {}%'.format(round(((margin/settings.init_margin-1) * 100),2)))
_logger.info('Stops: {}'.format(len(stops_reached)))
_logger.info('Targets: {}'.format(len(targets_reached)))
_logger.info('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
_logger.info('Mean Position Time {} min'.format(round(np.mean(position_time)*(resolution/60),2)))
_logger.info('-------------------------------')
_logger.info('///////////////////////////////')


from bokeh.io import output_notebook, show
from bokeh.plotting import figure
p = figure(plot_width=1800, plot_height=800)
p.line(ohlcv.datetime, ohlcv.Close, line_width=2, color = 'black',legend_label="Close Price")
# p.line(ohlcv.datetime, bb_top, line_width=2, color = 'orange', legend_label="BBands HBand")
# p.line(ohlcv.datetime, bb_bottom, line_width=2, color = 'orange',legend_label="BBands LBand")

p.circle([x[0] for x in stops_reached], [x[1] for x in stops_reached], legend_label="Stop Loss Reached", fill_color="yellow", size=8)
p.circle([x[0] for x in targets_reached], [x[1] for x in targets_reached], legend_label="Profit Target Reached", fill_color="brown", size=8)

p.circle([x[0] for x in long_signals], [x[1] for x in long_signals], legend_label="Long Signal", fill_color="green", size=8)
p.circle([x[0] for x in short_signals], [x[1] for x in short_signals], legend_label="Short Signal", fill_color="red", size=8)
show(p)

# e = figure(plot_width=1800, plot_height=200)
# e.line(H1_ohlcv.datetime, RSI, line_width=2, color = 'black',legend_label="Close Price")
# show(e)