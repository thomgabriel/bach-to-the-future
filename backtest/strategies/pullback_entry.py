from tqdm import tqdm
import pandas as  pd
import talib as tb
import dateparser
import datetime as dt
import numpy as np

import backtest.util.tools as TOOLS
import backtest.util.logger as LOGGER
import backtest.util.settings as SETTINGS
from backtest.util.api_ftx import FtxClient

class PullbackEntry:

    def __init__(self):
        
        self.ohlcv = self.get_data()
        self.indicators = self.calc_indicators()

        self.pbar = tqdm(total=len(self.ohlcv))

        ##### Init Variables #####
        self.margin = SETTINGS.INIT_MARGIN

        self.stops_reached = []
        self.targets_reached = []
        self.short_signals = []
        self.long_signals = []
        self.partial_reached = []
        self.all_exec = []
        self.margin_returns = [(self.margin, self.ohlcv.datetime.iloc[100], 'Init Margin')]

        self.entry_time = 0
        self.position_time = []

        self.state_long = 0
        self.state_short = 0

        # self.target = 0
        self.stop= 0
        self.entry = 0
        self.qtd = 0

        ##### State Machine #####
        self.reached_stop = False
        self.reached_target = False
        self.in_long = False
        self.in_short = False
        self.partial_tgt = False


    def get_data(self):
        ftx = FtxClient()
        market_name = 'BTC-PERP'
        resolution = 900 # TimeFrame in seconds.
        limit = 10000
        start_time = (dt.datetime.fromisoformat('2020-07-05 00:00:00') - dt.timedelta(seconds=resolution*100)).timestamp()
        end_time = dt.datetime.now().timestamp()

        ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
        ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]
        ohlcv.datetime = ohlcv.datetime.apply(lambda x: dateparser.parse(x[:18]))
        return ohlcv

    def calc_indicators(self):
        """
        Return a dict of formatted indicators.
        Returns:
            indicators (list_of_dicts): with the following structure
            {
            'RSI': pandas.Series,
            'ma50' : pandas.Series,
            'ma20' : pandas.Series,
            'ma7' : pandas.Series,
            'bb_top' : pandas.Series,
            'bb_bottom' : pandas.Series,
            'macdz_hist' : pandas.Series,
            'linreg' : pandas.Series,
            'ATR' : pandas.Series,
            'bb_diff' : pandas.Series,
             }
        """

        # //Relative Strength Index calculation
        RSI = tb.RSI(self.ohlcv.Close, SETTINGS.PARAM_RSI)

        # //Simple Moving Averages calculation
        ma50 = tb.SMA(self.ohlcv.Close,SETTINGS.PARAM_MA50)
        ma20 = tb.SMA(self.ohlcv.Close,SETTINGS.PARAM_MA20)
        ma7 = tb.SMA(self.ohlcv.Close,SETTINGS.PARAM_MA7)

        # //Bollinger Bands calculation
        bb_top, bb_mid, bb_bottom = tb.BBANDS(self.ohlcv.Close, timeperiod=SETTINGS.PARAM_BB)
        bb_diff = (bb_top - bb_bottom)

        # //MACD's Fast EMA line calculation
        ema1= tb.EMA(self.ohlcv.Close,SETTINGS.PARAM_EMA1)
        ema2= tb.EMA(ema1,SETTINGS.PARAM_EMA2)
        differenceFast = ema1 - ema2
        zerolagEMA = ema1 + differenceFast
        demaFast = (2 * ema1) - ema2

        # //MACD's Slow EMA line calculation
        emas1= tb.EMA(self.ohlcv.Close,SETTINGS.PARAM_EMAS1)
        emas2 = tb.EMA(emas1,SETTINGS.PARAM_EMAS2)
        differenceSlow = emas1 - emas2
        zerolagslowMA = emas1 + differenceSlow
        demaSlow = (2 * emas1) - emas2

        # //MACD LINE calculation
        ZeroLagMACD = demaFast - demaSlow

        # //MACD's EMA Signal line calculation
        emasig1 = tb.EMA(ZeroLagMACD,SETTINGS.PARAM_EMASIG1)
        emasig2 = tb.EMA(emasig1,SETTINGS.PARAM_EMASIG2)
        signal = (2 * emasig1) - emasig2
        macdz_hist = ZeroLagMACD -signal
 
        # //LINEAR REGRESSION calculation
        linreg = tb.LINEARREG(ma50,SETTINGS.PARAM_LINREG)

        # //ATR calculation
        ATR = tb.ATR(high=self.ohlcv.High, low=self.ohlcv.Low, close= self.ohlcv.Close, timeperiod=SETTINGS.PARAM_ATR)
        
        indicators = {
            'RSI': RSI,
            'ma50' : ma50,
            'ma20' : ma20,
            'ma7' : ma7,
            'bb_top' : bb_top,
            'bb_bottom' : bb_bottom,
            'macdz_hist' : macdz_hist,
            'linreg' : linreg,
            'ATR' : ATR,
            'bb_diff' : bb_diff,
             }
        return indicators

    def main_loop(self):
        indicators = self.calc_indicators()
        for num in range(100,len(self.ohlcv)):

            actualPrice = self.ohlcv.Close.iloc[num]
            high = self.ohlcv.High.iloc[num]
            low = self.ohlcv.Low.iloc[num]
            timestamp = self.ohlcv.datetime.iloc[num]

            RSI = indicators['RSI'].iloc[num]
            ma50 = indicators['ma50'].iloc[num]
            ma20 = indicators['ma20'].iloc[num]
            ma7 = indicators['ma7'].iloc[num]
            bb_top = indicators['bb_top'].iloc[num]
            bb_bottom = indicators['bb_bottom'].iloc[num]
            macdz_hist = indicators['macdz_hist'].iloc[num]
            linreg = indicators['linreg'].iloc[num]
            linreg_one_period = indicators['linreg'].iloc[num-1]
            ATR = indicators['ATR'].iloc[num]
            bb_confluency = all(np.diff(indicators['bb_diff'][num-6:num]) < 0)

            #Check Execution
            #in Long
            if self.in_long == True:
                if high >= bb_top and self.partial_tgt == False:
                    self.partial_tgt = True
                    self.margin = self.margin + ((self.qtd/self.entry - self.qtd/bb_top) - (self.qtd/bb_top * SETTINGS.MAKER_FEE)) *0.5
                    self.partial_reached.append((timestamp,self.entry, bb_top))
                    self.stop = self.entry
                    self.all_exec.append((timestamp, TOOLS.toNearest(bb_top), 'Partial Target'))
                    self.margin_returns.append((self.margin, timestamp, 'Partial Target'))

                elif RSI >= 75:
                    if self.partial_tgt == True:
                        self.reached_target = True
                        self.in_long = False
                        self.margin = self.margin + ((self.qtd/self.entry - self.qtd/actualPrice) - (self.qtd/actualPrice * SETTINGS.TAKER_FEE))*0.5
                       
                    else:
                        self.reached_target = True
                        self.in_long = False
                        self.margin = self.margin + ((self.qtd/self.entry - self.qtd/actualPrice) - (self.qtd/actualPrice * SETTINGS.TAKER_FEE))
                        

                elif low <= self.stop:
                    if self.partial_tgt == True:
                        self.margin = self.margin + ((self.qtd/self.entry - self.qtd/self.stop) - (self.qtd/self.stop * SETTINGS.TAKER_FEE))*0.5
                        self.reached_stop = True
                        self.in_long = False
                
                    else:
                        self.reached_stop = True
                        self.in_long = False
                        self.margin = self.margin + ((self.qtd/self.entry) - (self.qtd/self.stop)) - (self.qtd/self.stop * SETTINGS.TAKER_FEE)


            if self.in_short == True:    
                if low <= bb_bottom and self.partial_tgt == False: 
                    self.partial_tgt = True
                    self.margin = self.margin + ((self.qtd/bb_bottom - self.qtd/self.entry) - (self.qtd/bb_bottom * SETTINGS.MAKER_FEE)) *0.5
                    self.partial_reached.append((timestamp,self.entry, bb_bottom))
                    self.stop = self.entry
                    self.all_exec.append((timestamp, TOOLS.toNearest(bb_bottom), 'Partial Target'))
                    self.margin_returns.append((self.margin, timestamp, 'Partial Target'))

                elif RSI <= 25:
                    if self.partial_tgt == True:
                        self.reached_target = True
                        self.in_short = False
                        self.margin = self.margin + ((self.qtd/actualPrice - self.qtd/self.entry) - (self.qtd/actualPrice * SETTINGS.TAKER_FEE)) *0.5
         
                    else:
                        self.reached_target = True
                        self.in_short = False
                        self.margin = self.margin + ((self.qtd/actualPrice - self.qtd/self.entry) - (self.qtd/actualPrice * SETTINGS.TAKER_FEE)) 


                elif high >= self.stop:
                    if self.partial_tgt == True:
                        self.margin = self.margin + ((self.qtd/self.stop - self.qtd/self.entry) - (self.qtd/self.stop * SETTINGS.TAKER_FEE)) *0.5
                        self.reached_stop = True
                        self.in_short = False
                    else:
                        self.margin = self.margin + ((self.qtd/self.stop - self.qtd/self.entry) - (self.qtd/self.stop * SETTINGS.TAKER_FEE))
                        self.reached_stop = True
                        self.in_short = False

            # If reached Stop Loss   
            if self.reached_stop:
                self.reached_stop = False
                self.partial_tgt = False

                self.position_time.append(num - self.entry_time)
                self.stops_reached.append((timestamp,self.entry, self.stop))
                self.all_exec.append((timestamp, self.stop, 'Stop Loss'))
                self.margin_returns.append((self.margin, timestamp, 'Stop Loss'))   

                self.state_short = 0
                self.state_long = 0

            # If reached Profit Target
            if self.reached_target:
                self.reached_target = False
                self.partial_tgt = False

                self.position_time.append(num - self.entry_time)
                self.targets_reached.append((timestamp,self.entry, actualPrice))
                self.all_exec.append((timestamp, actualPrice, 'Profit Target'))
                self.margin_returns.append((self.margin, timestamp, 'Profit Target'))

                self.state_short = 0
                self.state_long = 0

            if (not self.in_long) and (not self.in_short):
                
                # //Buy Sell Signal
                if self.state_long == 0 and self.state_short == 0:

                    if ma50 > (ma20 + (bb_top - ma20)/2):
                        ma50_near_BB= -1
                    elif ma50 < (ma20 - (ma20 - bb_bottom)/2):
                        ma50_near_BB= 1
                    else:
                        ma50_near_BB= 0

                    if high > (ma20+(bb_top - ma20)/2):
                        price_near_BB = -1
                    elif low < (ma20-(ma20 - bb_bottom)/2):
                        price_near_BB = 1
                    else:
                        price_near_BB= 0

                    if (linreg_one_period-linreg)/linreg > 0.0002:
                        ma_steepness = -1
                    elif (linreg_one_period-linreg)/linreg < -0.0002:
                        ma_steepness = 1
                    else:
                        ma_steepness = 0

                    if macdz_hist > 0:
                        macdz_direction = 1
                    else:
                        macdz_direction = -1

                    if ma50_near_BB >= 1  and macdz_direction >= 1 and price_near_BB >= 1 and ma_steepness >= 1: #BUY SIGNAL
                        self.state_long = 1
                    elif ma50_near_BB <= -1 and macdz_direction <= -1 and price_near_BB <= -1 and ma_steepness <= -1: #SELL SIGNAL
                        self.state_short = 1

                elif self.state_long:
                    if self.state_long == 1 and low <= bb_bottom:
                        if bb_confluency and RSI > 40: #and n_slope:
                            self.state_long = 2 
                            self.qtd = round(actualPrice * self.margin * SETTINGS.LEVAREGE)
                            self.entry = actualPrice -1

                    if self.state_long == 2 and low <= self.entry:
                        self.stop = TOOLS.toNearest(actualPrice - (ATR*2))
                        self.margin = self.margin - (self.qtd/self.entry * SETTINGS.MAKER_FEE)
                        self.in_long = True
                        self.entry_time = num
                        self.long_signals.append((timestamp, self.entry)) 
                        self.all_exec.append((timestamp, self.entry, 'Long Signal')) 
                
                elif self.state_short:
                    if self.state_short == 1 and high >= bb_top:
                        if bb_confluency and RSI < 65: # and (not n_slope):
                            self.state_short = 2
                            self.qtd = round(actualPrice * self.margin * SETTINGS.LEVAREGE)
                            self.entry = actualPrice +1

                    if self.state_short == 2 and high >= self.entry:
                        self.stop = TOOLS.toNearest(actualPrice + (ATR*2))
                        self.margin = self.margin - (self.qtd/self.entry * SETTINGS.MAKER_FEE)
                        self.in_short = True
                        self.entry_time = num
                        self.short_signals.append((timestamp, self.entry))
                        self.all_exec.append((timestamp, self.entry, 'Short Signal'))
                else:
                    self.state_short = 0
                    self.state_long = 0
                    
            self.pbar.update(1)
        self.pbar.close()
        return

    def calc_statistics(self):

        margin_returns = pd.DataFrame(data=self.margin_returns, columns=['data','datetime', 'type'])
        margin_returns['pct'] = margin_returns.data.pct_change()*100
        margin_returns['pct'].iloc[0] = 0

        statistics = {
                'Start': str(self.ohlcv.datetime.iloc[100]),
                'End' : str(self.ohlcv.datetime.iloc[-1]),
                'Final Margin' : round(self.margin,5),
                'Profit/loss' : '{}%' .format(round(((self.margin/SETTINGS.INIT_MARGIN-1) * 100),2)),
                "Stops Reached" : '{} ({}%)'.format(len(self.stops_reached),round((len(self.stops_reached)/(len(self.stops_reached)+len(self.targets_reached))*100))),
                'Target Reached' : '{} ({}%)'.format(len(self.targets_reached),round((len(self.targets_reached)/(len(self.stops_reached)+len(self.targets_reached))*100))),
                'Partial Target Reached' : '{} ({}%)'.format(len(self.partial_reached),round((len(self.partial_reached)/(len(self.stops_reached)+len(self.targets_reached))*100))),
                'Winrate' : '{}%'.format(round(len(self.targets_reached)/(len(self.targets_reached)+len(self.stops_reached))*100,2)),
                'Median Position Time' : '{} min'.format(round(np.median(self.position_time),2)),
                # 'Sharpe Ratio ' : round((margin_returns.pct.mean()/margin_returns.pct.std()),3)
            }
        return statistics
    
    def get_plot_data(self):
        data = dict(ohlcv = self.ohlcv,
            stops_reached = self.stops_reached,
            targets_reached = self.targets_reached,
            partial_reached = self.partial_reached,
            long_signals = self.long_signals,
            short_signals = self.short_signals,
            all_exec = self.all_exec,
            margin_returns = self.margin_returns,
            )
        return data

    def run_backtest(self):
        self.main_loop()
        return

if __name__ == "__main__":

    logger = LOGGER.setup_logger()
    statistics_logger = LOGGER.setup_db('../../data/statistics/statistics')

    a = PullbackEntry()
    a.run_backtest()
    statistics = a.calc_statistics()

    a.statistics_logger.info([(x, statistics[x]) for x in statistics])
    print('\n')
    for x in statistics:
        a.logger.info('{} : {}'.format(x, statistics[x]))
    print('\n')

