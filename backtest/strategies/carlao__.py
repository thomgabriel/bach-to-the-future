from tqdm import tqdm
import statistics as st
import json
from backtest.util.paralelism_test import loop_sorting_index as stort_indicator
import backtest.util.func as func
import backtest.util.tools as tools
import backtest.util.logger as logger
import time
import multiprocessing

start_time = time.time()
with open('../../data/candles.json') as f:
    candles = json.load(f)['candles']
closes = [x['close'] for x in candles] 
statistics_logger = logger.setup_db('../../../data/statistics/carlao_statistics')

##### Parameters #####
init_margin = 1.0
margin = init_margin
margins = []

leverage = 2
profit = 0.006 # +0.5% from market price
stop = 0.006
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
state_short = 0
state_long = 0

reached_stop = False
reached_target = False

in_long = False
in_short = False

sort_indicator= stort_indicator(closes)

# def loop(n):
#     print('Run num {}.format'.format(n))
    ##########################################
    ##### Parameters #####
init_margin = 1.0
margin = init_margin
margins = []

leverage = 1
profit = 0.006 # +0.5% from market price
stop = 0.006
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
state_short = 0
state_long = 0

reached_stop = False
reached_target = False

in_long = False
in_short = False
#######################################

# pbar = tqdm(total=len(closes))
Macd_short= func.MACD(closes,7,14,13)
Macd_long= func.MACD(closes,84,182,63)

for num,candle in enumerate(candles):

    actualPrice = candle['close']
    high = candle['high']
    low = candle['low']
    timestamp = candle['timestamp']

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
        state_short = 0
        state_long = 0
        reached_stop = False
        stops_reached.append([timestamp, actualPrice])
        leave_time = num
        position_time.append(leave_time - entry_time)

    # If reached Profit Target
    if reached_target:
        state_short = 0
        state_long = 0
        reached_target = False
        targets_reached.append([timestamp, actualPrice])
        leave_time = num
        position_time.append(leave_time - entry_time)

    if (not in_long) and (not in_short):
        
        # Long / Tendência de alta
        if Macd_long[num] > 0:
            # Condição necessária  (convergência: linhas de mesmo sinal)
            if Macd_short[num] > Macd_long[num] and state_long == 0 and sort_indicator[num] > 92:
                state_long = 1

            # Condição suficiente 1 (princípio da divergência) (sinal opostos)
            if Macd_short[num] < 0 and state_long == 1:
                
                long_qtd = round(actualPrice * margin * leverage * 0.1) # In contracts, entry only with 80% of available margin
                long_entry = actualPrice
                long_target = tools.toNearest(actualPrice + actualPrice * profit)
                long_stop = tools.toNearest(actualPrice - actualPrice * stop)
                in_long = True
                state_long = 2
                entry_time = num
                margin = margin - (long_qtd/long_entry * maker_fee)

        # Short / Tendência de queda
        elif Macd_long[num] < 0:
            # Condição necessária (convergência: linhas de mesmo sinal)
            if Macd_short[num]< Macd_long[num] and state_short == 0 and sort_indicator[num] < -92:
                state_short = 1

            #  %Condição suficiente 1 (princípio da divergência) (sinais opostos)
            if Macd_short[num] > 0 and state_short == 1:
                
                short_qtd = round(actualPrice * margin * leverage * 0.1) # In contracts, entry only with 80% of available margin
                short_entry = actualPrice
                short_target = tools.toNearest(actualPrice - actualPrice * profit)
                short_stop = tools.toNearest(actualPrice + actualPrice * stop)
                state_short = 2
                in_short = True
                entry_time = num
                margin = margin - (short_qtd/short_entry * maker_fee)
        else:
            state_short = 0
            state_long = 0

#     pbar.update(1)
# pbar.close()
#     return
    
# with multiprocessing.Pool(8) as pool:
#     pool.map(loop,range(0, 10))

# lopp_time = time.time() - start_time
# print(lopp_time)


# statistics_logger.info('Margin: {}, Profit/loss: {}, Stops: {}, Targets: {}'.format(round(margin,5),round((margin/init_margin) * 100,2),len(stops_reached),len(targets_reached)))
# statistics_logger.info('Stops: {}'.format(stops_reached))
# statistics_logger.info('Targets: {}'.format(targets_reached))
# statistics_logger.info('margins: {}'.format(margins))
# statistics_logger.info('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
# statistics_logger.info('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
# statistics_logger.info('(////////////////////////////////////////////////////////')

print('///////////////////////////////')
print('-------------------------------')
# print('Loop Run Time: {} seconds'.format(round(lopp_time,2)))
print('Start: {}'.format(candles[0]['timestamp']))
print('End: {}'.format(candles[-1]['timestamp']))
print('Final Margin: {}'.format(round(margin,5)))
print('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
print('Stops: {}'.format(len(stops_reached)))
print('Targets: {}'.format(len(targets_reached)))
print('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
print('Mean Position Time {} min'.format(round(st.mean(position_time),2)))
print('-------------------------------')
print('///////////////////////////////')