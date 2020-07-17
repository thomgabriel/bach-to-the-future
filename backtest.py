import tools
import csv
from tqdm import tqdm
import logger
import statistics as st

try:
    with open('data.csv' , 'r') as file:
        readcsv = csv.reader(file, delimiter=',')
        candles= [row for row in readcsv][0]
        candles= [float(x) for x in candles]
except:
    candles = []

try:
    with open('functions.csv', 'r') as file:
        readstatistic = csv.reader(file, delimiter=',')
        functions= [row for row in readstatistic]
        Macd_short= [float(x) for x in functions[0]]
        Macd_long= [float(x) for x in functions[1]]
        sort_indicator= [float(x) for x in functions[2]]
except:
    Macd_short = []
    Macd_long = []
    sort_indicator = []

pbar = tqdm(total=len(candles))
statistics_logger = logger.setup_db('statistics')

##### Parameters #####
init_margin = 1.0
margin = init_margin
margins = []

leverage = 5
profit = 0.005 # +0.5% from market price
stop = 0.005

taker_fee= -0.00075
maker_fee = 0.00025

entry_time = 0
leave_time = 0
position_time = []

##### State Machine #####
state_short = 0
state_long = 0

reached_stop = False
stops_reached = []

reached_target = False
targets_reached = []

in_long = False
long_target = 0
long_stop = 0
long_entry = 0
long_qtd = 0

in_short = False
short_target = 0
short_stop = 0
short_entry = 0
short_qtd = 0

for num,close in enumerate(candles):
    
    actualPrice = close
    
    #Check Execution
    #in Long
    if in_long == True:
        if actualPrice >= long_target:
            margin = margin + (long_target/long_entry-1) * (long_qtd/long_target) + (long_qtd/long_target * maker_fee)

            margins.append('L_target,{}'.format(margin))
            reached_target = True
            in_long = False

        if actualPrice <= long_stop:
            margin = margin - (1-long_stop/long_entry) * (long_qtd/long_stop) + (long_qtd/long_stop * taker_fee)

            margins.append('L_stop,{}'.format(margin))
            reached_stop = True
            in_long = False

    if in_short == True: 
        if actualPrice <= short_target:
            margin = margin + (1-short_target/short_entry) * (short_qtd/short_target) + (short_qtd/short_target * maker_fee)

            margins.append('S_target,{}'.format(margin))
            reached_target = True
            in_short = False

        if actualPrice >= short_stop:
            margin = margin - (short_stop/short_entry-1) * (short_qtd/short_stop) + (short_qtd/short_stop * taker_fee)

            margins.append('S_stop,{}'.format(margin))
            reached_stop = True
            in_short = False

    # If reached Stop Loss   
    if reached_stop:
        state_short = 0
        state_long = 0
        reached_stop = False
        stops_reached.append([num, close])
        leave_time = num
        position_time.append(leave_time - entry_time)

    # If reached Profit Target
    if reached_target:
        state_short = 0
        state_long = 0
        reached_target = False
        targets_reached.append([num, close])
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
                
                long_qtd = round(actualPrice * margin * leverage * 0.8) # In contracts, entry only with 80% of available margin
                long_entry = actualPrice
                long_target = tools.toNearest(actualPrice + actualPrice * profit)
                long_stop = tools.toNearest(actualPrice - actualPrice * stop)
                in_long = True
                state_long = 2

                # margin = margin + actualPrice/long_qtd * taker_fee
                margin = margin + actualPrice/long_qtd * maker_fee

                entry_time = num

        # Short / Tendência de queda
        elif Macd_long[num] < 0:
            # Condição necessária (convergência: linhas de mesmo sinal)
            if Macd_short[num]< Macd_long[num] and state_short == 0 and sort_indicator[num] < -92:
                state_short = 1

            #  %Condição suficiente 1 (princípio da divergência) (sinais opostos)
            if Macd_short[num] > 0 and state_short == 1:
                
                short_qtd = round(actualPrice * margin * leverage * 0.8) # In contracts, entry only with 80% of available margin
                short_entry = actualPrice
                short_target = tools.toNearest(actualPrice - actualPrice * profit)
                short_stop = tools.toNearest(actualPrice + actualPrice * stop)
                state_short = 2
                in_short = True

                # margin = margin + actualPrice/short_qtd * taker_fee
                margin = margin + actualPrice/short_qtd * maker_fee

                entry_time = num
        else:
            state_short = 0
            state_long = 0

    pbar.update(1)
pbar.close()

statistics_logger.info('Margin: {}, Profit/loss: {}, Stops: {}, Targets: {}'.format(round(margin,5),round((margin/init_margin) * 100,2),len(stops_reached),len(targets_reached)))
statistics_logger.info('Stops: {}'.format(stops_reached))
statistics_logger.info('Targets: {}'.format(targets_reached))
statistics_logger.info('margins: {}'.format(margins))
statistics_logger.info('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
statistics_logger.info('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
statistics_logger.info('(////////////////////////////////////////////////////////')

print('///////////////////////////////')
print('-------------------------------')
print('Final Margin: {}'.format(round(margin,5)))
print('Profit/loss: {}%'.format(round(((margin/init_margin-1) * 100),2)))
print('Stops: {}'.format(len(stops_reached)))
print('Targets: {}'.format(len(targets_reached)))
print('Winrate: {}%'.format(round(len(targets_reached)/(len(targets_reached)+len(stops_reached))*100,2)))
print('Mean Position Time {} min'.format(round(st.mean(position_time),2)))
print('-------------------------------')
print('///////////////////////////////')